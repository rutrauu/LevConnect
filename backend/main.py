"""
LevConnect - Backend API
Omnichannel CRM & Cross-Store Inventory Management for Fashion Retail (Lojas Lev)
"""

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random
import os
import uvicorn

import sys
import os

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import database as db

app = FastAPI(
    title="LevConnect API",
    description="Plataforma de CRM e Vendas Omnichannel para Varejo Regional (Lojas Lev)",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class MessageCreate(BaseModel):
    sender: str
    text: str
    type: Optional[str] = "text"
    payload: Optional[Dict[str, Any]] = None

class StatusUpdate(BaseModel):
    status: str

class CustomerUpdate(BaseModel):
    shoe_size: Optional[str] = None
    clothing_size_top: Optional[str] = None
    clothing_size_bottom: Optional[str] = None
    preferred_store: Optional[str] = None
    notes: Optional[str] = None
    favorite_brands: Optional[List[str]] = None

class ReservationCreate(BaseModel):
    customer_id: str
    product_id: str
    size: str
    pickup_store: str
    source_store: str
    chat_id: Optional[str] = None
    seller_name: Optional[str] = "Mariana Santos"
    notes: Optional[str] = ""

class SimulationRequest(BaseModel):
    scenario: Optional[str] = "charqueadas_bota"
    custom_customer_name: Optional[str] = None
    custom_message: Optional[str] = None

# --- API Endpoints ---

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "LevConnect", "version": "1.0.0"}

@app.get("/api/stores")
def get_stores():
    return {"stores": db.STORES}

@app.get("/api/sellers")
def get_sellers():
    return {"sellers": db.SELLERS}

@app.get("/api/chats")
def list_chats(status_filter: Optional[str] = None, search: Optional[str] = None):
    results = db.CHATS
    if status_filter and status_filter != "all":
        results = [c for c in results if c["status"] == status_filter]
    if search:
        s = search.lower()
        results = [c for c in results if s in c["customer_name"].lower() or s in c["customer_phone"]]
    return {"chats": results}

@app.get("/api/chats/{chat_id}")
def get_chat(chat_id: str):
    chat = next((c for c in db.CHATS if c["id"] == chat_id), None)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat não encontrado")
    
    # Mark messages as read
    chat["unread"] = 0
    
    # Get associated customer
    customer = next((cu for cu in db.CUSTOMERS if cu["id"] == chat["customer_id"]), None)
    
    # Get active reservations for customer
    customer_reservations = [r for r in db.RESERVATIONS if r["customer_id"] == chat["customer_id"]]
    
    return {
        "chat": chat,
        "customer": customer,
        "reservations": customer_reservations
    }

@app.post("/api/chats/{chat_id}/messages")
def send_message(chat_id: str, payload: MessageCreate):
    chat = next((c for c in db.CHATS if c["id"] == chat_id), None)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat não encontrado")
    
    now_str = datetime.now().strftime("%H:%M")
    new_msg = {
        "id": f"MSG-{int(datetime.now().timestamp() * 1000)}",
        "sender": payload.sender,
        "text": payload.text,
        "time": now_str,
        "type": payload.type,
        "payload": payload.payload
    }
    chat["messages"].append(new_msg)
    chat["last_message"] = payload.text
    chat["last_time"] = now_str
    
    return {"status": "success", "message": new_msg}

@app.patch("/api/chats/{chat_id}/status")
def update_chat_status(chat_id: str, payload: StatusUpdate):
    chat = next((c for c in db.CHATS if c["id"] == chat_id), None)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat não encontrado")
    chat["status"] = payload.status
    return {"status": "success", "chat_id": chat_id, "new_status": payload.status}

# --- Customers (Smart CRM) ---

@app.get("/api/customers")
def get_customers():
    return {"customers": db.CUSTOMERS}

@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str):
    customer = next((cu for cu in db.CUSTOMERS if cu["id"] == customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    reservations = [r for r in db.RESERVATIONS if r["customer_id"] == customer_id]
    return {"customer": customer, "reservations": reservations}

@app.put("/api/customers/{customer_id}")
def update_customer(customer_id: str, payload: CustomerUpdate):
    customer = next((cu for cu in db.CUSTOMERS if cu["id"] == customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    if payload.shoe_size is not None:
        customer["shoe_size"] = payload.shoe_size
    if payload.clothing_size_top is not None:
        customer["clothing_size_top"] = payload.clothing_size_top
    if payload.clothing_size_bottom is not None:
        customer["clothing_size_bottom"] = payload.clothing_size_bottom
    if payload.preferred_store is not None:
        customer["preferred_store"] = payload.preferred_store
    if payload.notes is not None:
        customer["notes"] = payload.notes
    if payload.favorite_brands is not None:
        customer["favorite_brands"] = payload.favorite_brands
        
    return {"status": "success", "customer": customer}

# --- Products & Cross-Store Stock ---

@app.get("/api/products")
def list_products(query: Optional[str] = None, category: Optional[str] = None):
    results = db.PRODUCTS
    if category and category != "all":
        results = [p for p in results if p["category"].lower() == category.lower()]
    if query:
        q = query.lower()
        results = [
            p for p in results 
            if q in p["name"].lower() or q in p["sku"].lower() or q in p["brand"].lower()
        ]
    return {"products": results}

@app.get("/api/products/{product_id}")
def get_product(product_id: str):
    product = next((p for p in db.PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return {"product": product}

# --- Reservations (Clique e Retire / Inter-Lojas) ---

@app.get("/api/reservations")
def list_reservations(store: Optional[str] = None, status_filter: Optional[str] = None):
    results = db.RESERVATIONS
    if store and store != "all":
        results = [r for r in results if r["pickup_store"] == store or r["source_store"] == store]
    if status_filter and status_filter != "all":
        results = [r for r in results if r["status"] == status_filter]
    return {"reservations": results}

@app.post("/api/reservations")
def create_reservation(payload: ReservationCreate):
    product = next((p for p in db.PRODUCTS if p["id"] == payload.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    customer = next((c for c in db.CUSTOMERS if c["id"] == payload.customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Check and decrement stock in source store
    source_stock = product["stock"].get(payload.source_store, {})
    current_qty = source_stock.get(payload.size, 0)
    if current_qty <= 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Saldo insuficiente ({current_qty}) no tamanho {payload.size} na filial {payload.source_store}"
        )
    
    # Decrement stock
    product["stock"][payload.source_store][payload.size] = current_qty - 1
    
    is_inter = (payload.pickup_store != payload.source_store)
    res_code = f"RES-{random.randint(9000, 9999)}"
    now = datetime.now()
    expires = now + timedelta(hours=48)
    
    new_res = {
        "id": res_code,
        "customer_id": customer["id"],
        "customer_name": customer["name"],
        "customer_phone": customer["phone"],
        "product_id": product["id"],
        "product_sku": product["sku"],
        "product_name": product["name"],
        "product_image": product["image"],
        "size": payload.size,
        "price": product["price"],
        "pickup_store": payload.pickup_store,
        "source_store": payload.source_store,
        "is_inter_store": is_inter,
        "status": "em_transito" if is_inter else "aguardando_separacao",
        "created_at": now.isoformat(),
        "expires_at": expires.isoformat(),
        "seller_name": payload.seller_name,
        "notes": payload.notes or ("Transferência inter-lojas solicitada" if is_inter else "Retirada local")
    }
    
    db.RESERVATIONS.insert(0, new_res)
    
    # If chat_id is provided, automatically post a voucher card into the conversation
    if payload.chat_id:
        chat = next((c for c in db.CHATS if c["id"] == payload.chat_id), None)
        if chat:
            chat["status"] = "reserved"
            voucher_msg = {
                "id": f"MSG-{int(datetime.now().timestamp() * 1000)}",
                "sender": "system",
                "text": f"Ordem de Reserva #{res_code} confirmada! Retirada em {payload.pickup_store}" + 
                        (f" (Transferência de {payload.source_store})" if is_inter else " (Estoque local)"),
                "time": now.strftime("%H:%M"),
                "type": "reservation_voucher",
                "payload": {
                    "res_id": res_code,
                    "product_name": product["name"],
                    "size": payload.size,
                    "price": f"R$ {product['price']:.2f}".replace(".", ","),
                    "pickup_store": payload.pickup_store,
                    "source_store": payload.source_store,
                    "is_inter_store": is_inter,
                    "expires_at": expires.strftime("%d/%m/%Y às %H:%M")
                }
            }
            chat["messages"].append(voucher_msg)
            chat["last_message"] = f"Reserva #{res_code} emitida com sucesso"
            chat["last_time"] = now.strftime("%H:%M")
            
    return {"status": "success", "reservation": new_res}

@app.patch("/api/reservations/{res_id}/status")
def update_reservation_status(res_id: str, payload: StatusUpdate):
    res = next((r for r in db.RESERVATIONS if r["id"] == res_id), None)
    if not res:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    res["status"] = payload.status
    return {"status": "success", "reservation": res}

# --- WhatsApp Simulation ---

@app.post("/api/simulate-incoming")
def simulate_incoming_message(payload: SimulationRequest):
    now = datetime.now()
    now_str = now.strftime("%H:%M")
    
    if payload.scenario == "charqueadas_bota":
        chat = next((c for c in db.CHATS if c["id"] == "CHAT-101"), None)
        text = "Oi Mariana! Meu marido vai passar aí em Charqueadas também, tem o tênis casual 41?"
        sender_name = "Juliana Silveira"
    elif payload.scenario == "patricia_novidade":
        chat = next((c for c in db.CHATS if c["id"] == "CHAT-102"), None)
        text = "Lucas, vi a jaqueta biker no stories! Consegue segurar o tamanho G pra mim até amanhã?"
        sender_name = "Patrícia Vargas"
    elif payload.scenario == "nova_cliente_rio_pardo":
        # Create a new conversation
        new_cust_id = f"CUST-00{len(db.CUSTOMERS) + 1}"
        new_cust = {
            "id": new_cust_id,
            "name": payload.custom_customer_name or "Gabriela Dornelles",
            "phone": "(51) 99654-3210",
            "city": "Rio Pardo",
            "preferred_store": "Rio Pardo",
            "avatar": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=150&q=80",
            "shoe_size": "36",
            "clothing_size_top": "P",
            "clothing_size_bottom": "36",
            "favorite_brands": ["Lev Collection"],
            "total_purchases": 1,
            "lifetime_value": 259.90,
            "vip_status": False,
            "notes": "Cliente nova vinda do anúncio do Instagram das Lojas Lev.",
            "history": []
        }
        db.CUSTOMERS.append(new_cust)
        
        new_chat_id = f"CHAT-{len(db.CHATS) + 101}"
        text = payload.custom_message or "Boa tarde! Gostei muito do vestido midi floral evasê. Vocês têm o tamanho P disponível para retirada aqui em Rio Pardo?"
        new_chat = {
            "id": new_chat_id,
            "customer_id": new_cust_id,
            "customer_name": new_cust["name"],
            "customer_phone": new_cust["phone"],
            "avatar": new_cust["avatar"],
            "assigned_seller": "Camila Oliveira",
            "seller_store": "Rio Pardo",
            "status": "open",
            "unread": 1,
            "last_message": text,
            "last_time": now_str,
            "messages": [
                {
                    "id": f"MSG-{int(now.timestamp() * 1000)}",
                    "sender": "customer",
                    "text": text,
                    "time": now_str,
                    "type": "text"
                }
            ]
        }
        db.CHATS.insert(0, new_chat)
        return {"status": "success", "chat_id": new_chat_id, "message": text}
    else:
        chat = db.CHATS[0]
        text = payload.custom_message or "Olá, gostaria de saber se vocês têm mais opções de calçados na loja!"
        sender_name = chat["customer_name"]
        
    chat["unread"] += 1
    chat["last_message"] = text
    chat["last_time"] = now_str
    chat["messages"].append({
        "id": f"MSG-{int(now.timestamp() * 1000)}",
        "sender": "customer",
        "text": text,
        "time": now_str,
        "type": "text"
    })
    
    return {"status": "success", "chat_id": chat["id"], "message": text}

# --- Executive / Store Dashboard ---

@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    total_chats = len(db.CHATS)
    active_chats = len([c for c in db.CHATS if c["status"] in ["open", "in_progress", "reserved"]])
    
    total_reservations = len(db.RESERVATIONS)
    inter_store_count = len([r for r in db.RESERVATIONS if r["is_inter_store"]])
    local_count = total_reservations - inter_store_count
    
    total_res_value = sum(r["price"] for r in db.RESERVATIONS)
    
    # Store performance metrics
    store_metrics = []
    for store in db.STORES:
        store_res = [r for r in db.RESERVATIONS if r["pickup_store"] == store]
        count = len(store_res)
        value = sum(r["price"] for r in store_res)
        store_metrics.append({
            "store": store,
            "reservations_count": count,
            "total_value": value,
            "sellers_count": len([s for s in db.SELLERS if s["store"] == store])
        })
        
    # Shoe size demands from registered customers
    shoe_sizes: Dict[str, int] = {}
    for c in db.CUSTOMERS:
        size = c.get("shoe_size", "N/D")
        shoe_sizes[size] = shoe_sizes.get(size, 0) + 1
        
    return {
        "kpis": {
            "avg_response_time": "2.4 min",
            "prev_response_time": "45 min",
            "response_improvement": "94.6%",
            "conversion_rate": "68.2%",
            "active_chats": active_chats,
            "total_reservations": total_reservations,
            "inter_store_reservations": inter_store_count,
            "local_reservations": local_count,
            "total_sales_pipeline": f"R$ {total_res_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "stores_connected": 5
        },
        "stores_ranking": sorted(store_metrics, key=lambda x: x["reservations_count"], reverse=True),
        "shoe_size_demand": shoe_sizes
    }

# Mount frontend static directory
frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
