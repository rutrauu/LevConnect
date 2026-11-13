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
import sys
import uvicorn

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import database as db

app = FastAPI(
    title="LevConnect API",
    description="Plataforma de CRM e Vendas Omnichannel para Varejo Regional (Lojas Lev)",
    version="2.0.0"
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

class CopilotRequest(BaseModel):
    chat_id: str
    active_store: Optional[str] = "Charqueadas"
    seller_name: Optional[str] = "Mariana Santos"

class VipCampaignRequest(BaseModel):
    product_id: str
    size: str
    active_store: Optional[str] = "Charqueadas"
    seller_name: Optional[str] = "Mariana Santos"

# --- API Endpoints ---

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "app": "LevConnect",
        "version": "2.0.0",
        "persistence": "SQLite3"
    }

@app.get("/api/database/status")
def database_status():
    return db.get_db_diagnostics()

@app.post("/api/database/reset")
def reset_database():
    db.init_db(force_reset=True)
    return {
        "status": "success",
        "message": "Banco de dados SQLite restaurado para o estado inicial de demonstração.",
        "diagnostics": db.get_db_diagnostics()
    }

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
    if chat.get("unread", 0) > 0:
        chat["unread"] = 0
        db.save_state_to_sqlite()
    
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
        "id": f"MSG-{int(datetime.now().timestamp() * 1000)}-{random.randint(10,99)}",
        "sender": payload.sender,
        "text": payload.text,
        "time": now_str,
        "type": payload.type,
        "payload": payload.payload
    }
    chat["messages"].append(new_msg)
    chat["last_message"] = payload.text
    chat["last_time"] = now_str
    db.save_state_to_sqlite()
    
    return {"status": "success", "message": new_msg}

@app.patch("/api/chats/{chat_id}/status")
def update_chat_status(chat_id: str, payload: StatusUpdate):
    chat = next((c for c in db.CHATS if c["id"] == chat_id), None)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat não encontrado")
    chat["status"] = payload.status
    db.save_state_to_sqlite()
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
        
    db.save_state_to_sqlite()
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

# --- Reservations & Inter-Store Malote Logistics ---

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
                "id": f"MSG-{int(datetime.now().timestamp() * 1000)}-{random.randint(10,99)}",
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
            
    db.save_state_to_sqlite()
    return {"status": "success", "reservation": new_res}

@app.patch("/api/reservations/{res_id}/status")
def update_reservation_status(res_id: str, payload: StatusUpdate):
    res = next((r for r in db.RESERVATIONS if r["id"] == res_id), None)
    if not res:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    
    old_status = res["status"]
    res["status"] = payload.status
    now_str = datetime.now().strftime("%H:%M")

    # Find customer chat to send automated WhatsApp logistics notifications
    chat = next((c for c in db.CHATS if c["customer_id"] == res["customer_id"]), None)
    auto_msg = None

    if chat and old_status != payload.status:
        if payload.status == "em_transito":
            text = (
                f"🚚 Atualização de Malote ({res['id']}): Sua peça '{res['product_name']}' (Tam {res['size']}) "
                f"saiu da filial {res['source_store']} e está em trânsito para {res['pickup_store']}!"
            )
            auto_msg = {
                "id": f"MSG-{int(datetime.now().timestamp() * 1000)}-{random.randint(10,99)}",
                "sender": "seller",
                "text": text,
                "time": now_str,
                "type": "text"
            }
        elif payload.status == "pronto_retirada":
            text = (
                f"🎉 Oba, {res['customer_name'].split()[0]}! Sua reserva #{res['id']} ({res['product_name']} - Tam {res['size']}) "
                f"já está separada no balcão da filial {res['pickup_store']} pronta para você provar e retirar!"
            )
            auto_msg = {
                "id": f"MSG-{int(datetime.now().timestamp() * 1000)}-{random.randint(10,99)}",
                "sender": "seller",
                "text": text,
                "time": now_str,
                "type": "text"
            }
        elif payload.status == "concluido":
            text = (
                f"✅ Retirada concluída na loja de {res['pickup_store']}! Muito obrigado por comprar nas Lojas Lev, "
                f"{res['customer_name'].split()[0]}! Esperamos que ame seu {res['product_name']}."
            )
            auto_msg = {
                "id": f"MSG-{int(datetime.now().timestamp() * 1000)}-{random.randint(10,99)}",
                "sender": "seller",
                "text": text,
                "time": now_str,
                "type": "text"
            }
            chat["status"] = "closed"

        if auto_msg:
            chat["messages"].append(auto_msg)
            chat["last_message"] = auto_msg["text"]
            chat["last_time"] = now_str

    db.save_state_to_sqlite()
    return {"status": "success", "reservation": res, "auto_notification": auto_msg}

# --- Lev AI Copilot (Smart Fashion & Cross-Store Recommendation) ---

@app.post("/api/copilot/suggest")
def copilot_suggest(payload: CopilotRequest):
    chat = next((c for c in db.CHATS if c["id"] == payload.chat_id), None)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat não encontrado")
    
    customer = next((cu for cu in db.CUSTOMERS if cu["id"] == chat["customer_id"]), None)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    pickup_store = customer.get("preferred_store") or payload.active_store or "Charqueadas"
    shoe_size = customer.get("shoe_size", "37")
    top_size = customer.get("clothing_size_top", "M")
    first_name = customer["name"].split()[0]

    # Analyze last customer message for product keywords
    customer_msgs = [m["text"].lower() for m in chat.get("messages", []) if m.get("sender") == "customer"]
    last_text = customer_msgs[-1] if customer_msgs else ""

    primary_product = None
    for p in db.PRODUCTS:
        keywords = [w.lower() for w in p["name"].split() if len(w) > 3]
        if any(k in last_text for k in keywords):
            primary_product = p
            break

    if not primary_product:
        # Default to matching customer's category preference
        primary_product = db.PRODUCTS[0]

    target_size = shoe_size if primary_product["type"] == "shoes" else top_size
    if target_size not in primary_product["sizes"]:
        target_size = primary_product["sizes"][0]

    local_qty = primary_product["stock"].get(pickup_store, {}).get(target_size, 0)
    other_stores = [
        st for st in db.STORES
        if st != pickup_store and primary_product["stock"].get(st, {}).get(target_size, 0) > 0
    ]

    # Pick a cross-sell item from the opposite category to complete the look
    opposite_type = "clothing" if primary_product["type"] == "shoes" else "shoes"
    cross_sell_product = next((p for p in db.PRODUCTS if p["type"] == opposite_type), db.PRODUCTS[2])
    cross_size = top_size if cross_sell_product["type"] == "clothing" else shoe_size
    if cross_size not in cross_sell_product["sizes"]:
        cross_size = cross_sell_product["sizes"][0]

    if local_qty > 0:
        availability_phrase = (
            f"Acabei de conferir no estoque de {pickup_store} e temos {local_qty} unidade(s) "
            f"de *{primary_product['name']}* na sua numeração exata (*{target_size}*) pronta para você provar hoje!"
        )
        recommended_source = pickup_store
    elif other_stores:
        best_source = other_stores[0]
        source_qty = primary_product["stock"][best_source][target_size]
        availability_phrase = (
            f"Verifiquei no nosso sistema integrado: a numeração *{target_size}* de *{primary_product['name']}* "
            f"esgotou aqui em {pickup_store}, mas temos *{source_qty} par(es)/peça(s) na filial de {best_source}*! "
            f"Posso pedir a transferência gratuita pelo malote para você retirar e provar aqui em {pickup_store}."
        )
        recommended_source = best_source
    else:
        availability_phrase = (
            f"Consultei as 5 filiais e a numeração {target_size} de {primary_product['name']} acabou de esgotar, "
            f"mas posso separar uma opção similar na sua medida!"
        )
        recommended_source = pickup_store

    cross_sell_phrase = (
        f"💡 *Dica de Look Completo:* Como sei que você veste *{cross_size}* e adora {', '.join(customer.get('favorite_brands', ['Lev Collection'])[:2])}, "
        f"essa peça combina perfeitamente com *{cross_sell_product['name']}* (R$ {cross_sell_product['price']:.2f}). Quer que eu separe as duas juntas no seu Clique & Retire?"
    ).replace(".", ",")

    suggested_reply = f"Oi {first_name}! ✨ {availability_phrase} {cross_sell_phrase}"

    return {
        "status": "success",
        "customer_summary": {
            "name": customer["name"],
            "preferred_store": pickup_store,
            "shoe_size": shoe_size,
            "clothing_size_top": top_size,
            "vip": customer.get("vip_status", False)
        },
        "primary_recommendation": {
            "product_id": primary_product["id"],
            "name": primary_product["name"],
            "sku": primary_product["sku"],
            "price": primary_product["price"],
            "image": primary_product["image"],
            "size": target_size,
            "pickup_store": pickup_store,
            "source_store": recommended_source,
            "is_inter_store": (recommended_source != pickup_store),
            "local_qty": local_qty
        },
        "cross_sell_recommendation": {
            "product_id": cross_sell_product["id"],
            "name": cross_sell_product["name"],
            "sku": cross_sell_product["sku"],
            "price": cross_sell_product["price"],
            "image": cross_sell_product["image"],
            "size": cross_size
        },
        "suggested_reply": suggested_reply
    }

# --- Active CRM: VIP Campaign by Size ---

@app.get("/api/crm/vip-matches")
def get_vip_matches(product_id: str, size: str):
    product = next((p for p in db.PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    matches = []
    for c in db.CUSTOMERS:
        cust_size = c.get("shoe_size") if product["type"] == "shoes" else c.get("clothing_size_top")
        if cust_size == size:
            matches.append(c)

    return {
        "product": product["name"],
        "size": size,
        "matches_count": len(matches),
        "customers": matches
    }

@app.post("/api/crm/vip-campaign")
def send_vip_campaign(payload: VipCampaignRequest):
    product = next((p for p in db.PRODUCTS if p["id"] == payload.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    matching_customers = []
    for c in db.CUSTOMERS:
        cust_size = c.get("shoe_size") if product["type"] == "shoes" else c.get("clothing_size_top")
        if cust_size == payload.size:
            matching_customers.append(c)

    if not matching_customers:
        # Fallback to VIP customers if no exact size match
        matching_customers = [c for c in db.CUSTOMERS if c.get("vip_status")]

    now_str = datetime.now().strftime("%H:%M")
    notified_chats = []

    for cust in matching_customers:
        chat = next((ch for ch in db.CHATS if ch["customer_id"] == cust["id"]), None)
        if not chat:
            chat = {
                "id": f"CHAT-{len(db.CHATS) + 105}",
                "customer_id": cust["id"],
                "customer_name": cust["name"],
                "customer_phone": cust["phone"],
                "avatar": cust.get("avatar", ""),
                "assigned_seller": payload.seller_name or "Mariana Santos",
                "seller_store": cust.get("preferred_store", payload.active_store),
                "status": "in_progress",
                "unread": 0,
                "last_message": "",
                "last_time": now_str,
                "messages": []
            }
            db.CHATS.insert(0, chat)

        first_name = cust["name"].split()[0]
        price_fmt = f"R$ {product['price']:.2f}".replace(".", ",")
        campaign_text = (
            f"🌟 *Alerta VIP Lojas Lev para {first_name}:* Lembrei de você! Temos *{product['name']}* "
            f"disponível exatamente na sua numeração (*{payload.size}*) por {price_fmt}. "
            f"Quer que eu já deixe reservado no Clique & Retire da loja de {cust.get('preferred_store', payload.active_store)}?"
        )

        msg = {
            "id": f"MSG-{int(datetime.now().timestamp() * 1000)}-{random.randint(10,99)}",
            "sender": "seller",
            "text": campaign_text,
            "time": now_str,
            "type": "product_card",
            "payload": {
                "product_id": product["id"],
                "name": product["name"],
                "sku": product["sku"],
                "price": product["price"],
                "image": product["image"]
            }
        }
        chat["messages"].append(msg)
        chat["last_message"] = f"🎯 Oferta VIP Tam {payload.size}: {product['name']}"
        chat["last_time"] = now_str
        notified_chats.append({"chat_id": chat["id"], "customer_name": cust["name"]})

    db.save_state_to_sqlite()
    return {
        "status": "success",
        "sent_count": len(notified_chats),
        "notified": notified_chats
    }

# --- WhatsApp Simulation ---

@app.post("/api/simulate-incoming")
def simulate_incoming_message(payload: SimulationRequest):
    now = datetime.now()
    now_str = now.strftime("%H:%M")
    
    if payload.scenario == "charqueadas_bota":
        chat = next((c for c in db.CHATS if c["id"] == "CHAT-101"), None)
        text = "Oi Mariana! Meu marido vai passar aí em Charqueadas também, tem o tênis casual 37 ou 40?"
        sender_name = "Juliana Silveira"
    elif payload.scenario == "patricia_novidade":
        chat = next((c for c in db.CHATS if c["id"] == "CHAT-102"), None)
        text = "Lucas, vi a jaqueta biker no stories! Consegue segurar o tamanho G pra mim até amanhã?"
        sender_name = "Patrícia Vargas"
    elif payload.scenario == "nova_cliente_rio_pardo":
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
                    "id": f"MSG-{int(now.timestamp() * 1000)}-{random.randint(10,99)}",
                    "sender": "customer",
                    "text": text,
                    "time": now_str,
                    "type": "text"
                }
            ]
        }
        db.CHATS.insert(0, new_chat)
        db.save_state_to_sqlite()
        return {"status": "success", "chat_id": new_chat_id, "message": text}
    else:
        chat = db.CHATS[0]
        text = payload.custom_message or "Olá, gostaria de saber se vocês têm mais opções de calçados na loja!"
        sender_name = chat["customer_name"]
        
    chat["unread"] += 1
    chat["last_message"] = text
    chat["last_time"] = now_str
    chat["messages"].append({
        "id": f"MSG-{int(now.timestamp() * 1000)}-{random.randint(10,99)}",
        "sender": "customer",
        "text": text,
        "time": now_str,
        "type": "text"
    })
    db.save_state_to_sqlite()
    
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
        "shoe_size_demand": shoe_sizes,
        "db_diagnostics": db.get_db_diagnostics()
    }

# Mount frontend static directory
frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
