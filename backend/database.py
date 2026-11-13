"""
LevConnect - Relational SQLite Database & State Management
Case Study: Lojas Lev (Minas do Leão, Charqueadas, Encruzilhada do Sul, Pantâno Grande, Rio Pardo)
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "levconnect.db")

STORES = [
    "Charqueadas",
    "Minas do Leão",
    "Encruzilhada do Sul",
    "Pantâno Grande",
    "Rio Pardo"
]

INITIAL_SELLERS = [
    {
        "id": "SEL-01",
        "name": "Mariana Santos",
        "store": "Charqueadas",
        "role": "Vendedora Digital",
        "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=150&q=80"
    },
    {
        "id": "SEL-02",
        "name": "Lucas Pereira",
        "store": "Minas do Leão",
        "role": "Vendedor Balcão & Whats",
        "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&q=80"
    },
    {
        "id": "SEL-03",
        "name": "Camila Oliveira",
        "store": "Rio Pardo",
        "role": "Gerente de Atendimento",
        "avatar": "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=150&q=80"
    },
    {
        "id": "SEL-04",
        "name": "Rodrigo Silva",
        "store": "Pantâno Grande",
        "role": "Vendedor Omnichannel",
        "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=150&q=80"
    },
    {
        "id": "SEL-05",
        "name": "Fernanda Souza",
        "store": "Encruzilhada do Sul",
        "role": "Consultora de Moda",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80"
    }
]

INITIAL_CUSTOMERS = [
    {
        "id": "CUST-001",
        "name": "Juliana Silveira",
        "phone": "(51) 99842-1209",
        "city": "Charqueadas",
        "preferred_store": "Charqueadas",
        "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=150&q=80",
        "shoe_size": "37",
        "clothing_size_top": "M",
        "clothing_size_bottom": "38",
        "favorite_brands": ["Via Marte", "Lev Collection", "Arezzo"],
        "total_purchases": 8,
        "lifetime_value": 2450.00,
        "vip_status": True,
        "notes": "Cliente assídua. Prefere calçados confortáveis e sempre retira na loja de Charqueadas após o trabalho (por volta das 18h30).",
        "history": [
            {"date": "2026-09-14", "item": "Sandália Salto Bloco Nude (37)", "price": 189.90, "store": "Charqueadas"},
            {"date": "2026-08-02", "item": "Vestido Midi Floral (M)", "price": 249.90, "store": "Charqueadas"},
            {"date": "2026-06-19", "item": "Calça Jeans Wide Leg (38)", "price": 199.90, "store": "Charqueadas"}
        ]
    },
    {
        "id": "CUST-002",
        "name": "Patrícia Vargas",
        "phone": "(51) 98721-4355",
        "city": "Minas do Leão",
        "preferred_store": "Minas do Leão",
        "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=150&q=80",
        "shoe_size": "38",
        "clothing_size_top": "G",
        "clothing_size_bottom": "42",
        "favorite_brands": ["Lev Collection", "Vizzano", "Colcci"],
        "total_purchases": 5,
        "lifetime_value": 1340.00,
        "vip_status": False,
        "notes": "Gosta de novidades em vestidos e jaquetas. Prefere contato nas terças e quintas.",
        "history": [
            {"date": "2026-07-22", "item": "Jaqueta Biker Couro (G)", "price": 329.90, "store": "Minas do Leão"},
            {"date": "2026-05-10", "item": "Tênis Casual Branco (38)", "price": 229.90, "store": "Minas do Leão"}
        ]
    },
    {
        "id": "CUST-003",
        "name": "Matheus Bittencourt",
        "phone": "(51) 99134-8877",
        "city": "Rio Pardo",
        "preferred_store": "Rio Pardo",
        "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80",
        "shoe_size": "40",
        "clothing_size_top": "GG",
        "clothing_size_bottom": "44",
        "favorite_brands": ["Lev Man", "Reserva", "Osklen"],
        "total_purchases": 3,
        "lifetime_value": 890.00,
        "vip_status": False,
        "notes": "Costuma comprar presentes para a esposa e calçados casuais para si.",
        "history": [
            {"date": "2026-09-01", "item": "Tênis Casual Couro (40)", "price": 259.90, "store": "Rio Pardo"}
        ]
    },
    {
        "id": "CUST-004",
        "name": "Beatriz Zimmermann",
        "phone": "(51) 99312-7654",
        "city": "Encruzilhada do Sul",
        "preferred_store": "Encruzilhada do Sul",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80",
        "shoe_size": "36",
        "clothing_size_top": "P",
        "clothing_size_bottom": "36",
        "favorite_brands": ["Farm", "Arezzo", "Lev Collection"],
        "total_purchases": 11,
        "lifetime_value": 3120.00,
        "vip_status": True,
        "notes": "Cliente premium. Frequenta eventos regionais e sempre pede looks completos combinando calçado e vestido.",
        "history": [
            {"date": "2026-09-28", "item": "Vestido Midi Floral (P)", "price": 249.90, "store": "Encruzilhada do Sul"},
            {"date": "2026-08-15", "item": "Sandália Salto Bloco (36)", "price": 189.90, "store": "Encruzilhada do Sul"}
        ]
    },
    {
        "id": "CUST-005",
        "name": "Carla Mendonça",
        "phone": "(51) 98112-9921",
        "city": "Pantâno Grande",
        "preferred_store": "Pantâno Grande",
        "avatar": "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=150&q=80",
        "shoe_size": "38",
        "clothing_size_top": "M",
        "clothing_size_bottom": "40",
        "favorite_brands": ["Via Marte", "Lev Collection"],
        "total_purchases": 2,
        "lifetime_value": 479.80,
        "vip_status": False,
        "notes": "Novo cadastro via Instagram. Pediu informações sobre reserva para retirar na loja de Pantâno Grande.",
        "history": []
    }
]

INITIAL_PRODUCTS = [
    {
        "id": "PROD-001",
        "sku": "BOT-CTR-01",
        "name": "Bota Coturno Couro Tratorada",
        "category": "Calçados",
        "brand": "Lev Shoes & Vizzano",
        "price": 289.90,
        "image": "/assets/bota-coturno.jpg",
        "description": "Bota cano médio com solado tratorado robusto, zíper lateral para calce fácil e acabamento em couro legítimo fosco. Tendência absoluta de inverno e meia-estação.",
        "type": "shoes",
        "sizes": ["35", "36", "37", "38", "39"],
        "stock": {
            "Charqueadas": {"35": 2, "36": 3, "37": 0, "38": 4, "39": 1},
            "Minas do Leão": {"35": 1, "36": 0, "37": 3, "38": 2, "39": 0},
            "Encruzilhada do Sul": {"35": 0, "36": 2, "37": 2, "38": 1, "39": 2},
            "Pantâno Grande": {"35": 2, "36": 1, "37": 0, "38": 3, "39": 1},
            "Rio Pardo": {"35": 1, "36": 2, "37": 4, "38": 0, "39": 2}
        }
    },
    {
        "id": "PROD-002",
        "sku": "TEN-CAS-02",
        "name": "Tênis Casual Couro Minimalista",
        "category": "Calçados",
        "brand": "Lev Shoes",
        "price": 239.90,
        "image": "/assets/tenis-casual.jpg",
        "description": "Tênis casual clássico todo em couro macio branco com solado blaqueado. Perfeito para o dia a dia, combina com alfaiataria ou jeans.",
        "type": "shoes",
        "sizes": ["35", "36", "37", "38", "39", "40"],
        "stock": {
            "Charqueadas": {"35": 1, "36": 4, "37": 2, "38": 0, "39": 3, "40": 2},
            "Minas do Leão": {"35": 2, "36": 1, "37": 3, "38": 4, "39": 1, "40": 0},
            "Encruzilhada do Sul": {"35": 0, "36": 3, "37": 1, "38": 2, "39": 0, "40": 1},
            "Pantâno Grande": {"35": 3, "36": 0, "37": 2, "38": 1, "39": 2, "40": 2},
            "Rio Pardo": {"35": 2, "36": 2, "37": 0, "38": 3, "39": 1, "40": 3}
        }
    },
    {
        "id": "PROD-003",
        "sku": "VES-MID-03",
        "name": "Vestido Midi Floral Evasê",
        "category": "Vestuário",
        "brand": "Lev Collection",
        "price": 259.90,
        "image": "/assets/vestido-midi.jpg",
        "description": "Vestido midi com estampa floral botânica exclusiva, mangas fluidas levemente bufantes e faixa para amarração na cintura. Tecido leve de caimento impecável.",
        "type": "clothing",
        "sizes": ["P", "M", "G", "GG"],
        "stock": {
            "Charqueadas": {"P": 1, "M": 0, "G": 2, "GG": 1},
            "Minas do Leão": {"P": 2, "M": 3, "G": 1, "GG": 0},
            "Encruzilhada do Sul": {"P": 0, "M": 2, "G": 0, "GG": 2},
            "Pantâno Grande": {"P": 1, "M": 1, "G": 3, "GG": 1},
            "Rio Pardo": {"P": 3, "M": 2, "G": 1, "GG": 0}
        }
    },
    {
        "id": "PROD-004",
        "sku": "JAQ-COU-04",
        "name": "Jaqueta Biker Couro Sintético",
        "category": "Vestuário",
        "brand": "Lev Collection",
        "price": 349.90,
        "image": "/assets/jaqueta-couro.jpg",
        "description": "Jaqueta estilo biker com zíperes metálicos reforçados, forro térmico suave e corte estruturado moderno.",
        "type": "clothing",
        "sizes": ["P", "M", "G", "GG"],
        "stock": {
            "Charqueadas": {"P": 2, "M": 2, "G": 0, "GG": 1},
            "Minas do Leão": {"P": 1, "M": 1, "G": 2, "GG": 0},
            "Encruzilhada do Sul": {"P": 3, "M": 0, "G": 1, "GG": 2},
            "Pantâno Grande": {"P": 0, "M": 2, "G": 1, "GG": 0},
            "Rio Pardo": {"P": 1, "M": 3, "G": 2, "GG": 1}
        }
    },
    {
        "id": "PROD-005",
        "sku": "SAN-BLO-05",
        "name": "Sandália Salto Bloco Nude",
        "category": "Calçados",
        "brand": "Lev Shoes & Arezzo",
        "price": 199.90,
        "image": "/assets/sandalia-bloco.jpg",
        "description": "Sandália com tiras delicadas e salto bloco de 6cm. Palmilha ultra confort ideal para festas ou uso prolongado.",
        "type": "shoes",
        "sizes": ["35", "36", "37", "38", "39"],
        "stock": {
            "Charqueadas": {"35": 2, "36": 1, "37": 3, "38": 2, "39": 0},
            "Minas do Leão": {"35": 0, "36": 2, "37": 1, "38": 0, "39": 2},
            "Encruzilhada do Sul": {"35": 1, "36": 0, "37": 2, "38": 3, "39": 1},
            "Pantâno Grande": {"35": 2, "36": 3, "37": 0, "38": 1, "39": 0},
            "Rio Pardo": {"35": 1, "36": 1, "37": 2, "38": 2, "39": 1}
        }
    }
]

INITIAL_RESERVATIONS = [
    {
        "id": "RES-8901",
        "customer_id": "CUST-001",
        "customer_name": "Juliana Silveira",
        "customer_phone": "(51) 99842-1209",
        "product_id": "PROD-001",
        "product_sku": "BOT-CTR-01",
        "product_name": "Bota Coturno Couro Tratorada",
        "product_image": "/assets/bota-coturno.jpg",
        "size": "37",
        "price": 289.90,
        "pickup_store": "Charqueadas",
        "source_store": "Minas do Leão",
        "is_inter_store": True,
        "status": "em_transito",
        "created_at": "2026-10-08T09:15:00",
        "expires_at": "2026-10-10T19:00:00",
        "seller_name": "Mariana Santos",
        "notes": "Cliente quer provar após as 18h. Peça saindo de Minas do Leão via malote matutino."
    },
    {
        "id": "RES-8894",
        "customer_id": "CUST-002",
        "customer_name": "Patrícia Vargas",
        "customer_phone": "(51) 98721-4355",
        "product_id": "PROD-004",
        "product_sku": "JAQ-COU-04",
        "product_name": "Jaqueta Biker Couro Sintético",
        "product_image": "/assets/jaqueta-couro.jpg",
        "size": "G",
        "price": 349.90,
        "pickup_store": "Minas do Leão",
        "source_store": "Minas do Leão",
        "is_inter_store": False,
        "status": "pronto_retirada",
        "created_at": "2026-10-07T16:30:00",
        "expires_at": "2026-10-09T18:30:00",
        "seller_name": "Lucas Pereira",
        "notes": "Separado no balcão principal com etiqueta de reserva."
    },
    {
        "id": "RES-8870",
        "customer_id": "CUST-004",
        "customer_name": "Beatriz Zimmermann",
        "customer_phone": "(51) 99312-7654",
        "product_id": "PROD-003",
        "product_sku": "VES-MID-03",
        "product_name": "Vestido Midi Floral Evasê",
        "product_image": "/assets/vestido-midi.jpg",
        "size": "P",
        "price": 259.90,
        "pickup_store": "Encruzilhada do Sul",
        "source_store": "Rio Pardo",
        "is_inter_store": True,
        "status": "concluido",
        "created_at": "2026-10-05T11:00:00",
        "expires_at": "2026-10-07T19:00:00",
        "seller_name": "Fernanda Souza",
        "notes": "Retirado e pago no cartão da loja. Cliente elogiou a velocidade da transferência."
    }
]

INITIAL_CHATS = [
    {
        "id": "CHAT-101",
        "customer_id": "CUST-001",
        "customer_name": "Juliana Silveira",
        "customer_phone": "(51) 99842-1209",
        "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=150&q=80",
        "assigned_seller": "Mariana Santos",
        "seller_store": "Charqueadas",
        "status": "reserved",
        "unread": 0,
        "last_message": "Perfeito Mariana! Já reservei para você provar hoje.",
        "last_time": "09:42",
        "messages": [
            {
                "id": "MSG-1",
                "sender": "customer",
                "text": "Olá Mariana, bom dia! Vi no Instagram da Lev aquela bota coturno tratorada preta. Vocês têm o tamanho 37 aí na loja de Charqueadas?",
                "time": "09:12",
                "type": "text"
            },
            {
                "id": "MSG-2",
                "sender": "seller",
                "text": "Bom dia, Ju! Que bom falar contigo! Deixa eu verificar aqui no sistema em tempo real.",
                "time": "09:14",
                "type": "text"
            },
            {
                "id": "MSG-3",
                "sender": "seller",
                "text": "Consultando o estoque das 5 lojas: o 37 esgotou ontem aqui em Charqueadas, MAS temos 3 pares em Minas do Leão e 4 em Rio Pardo! Posso solicitar a transferência agora mesmo para cá?",
                "time": "09:16",
                "type": "text"
            },
            {
                "id": "MSG-4",
                "sender": "customer",
                "text": "Nossa, sério? Que maravilha! Chega a tempo de eu provar hoje no fim da tarde?",
                "time": "09:20",
                "type": "text"
            },
            {
                "id": "MSG-5",
                "sender": "seller",
                "text": "Sim! O carro do malote passa em Minas do Leão e chega aqui por volta das 16h. Já vou gerar seu voucher de reserva Clique & Retire!",
                "time": "09:23",
                "type": "text"
            },
            {
                "id": "MSG-6",
                "sender": "system",
                "text": "Ordem de Reserva #RES-8901 gerada com sucesso! Produto: Bota Coturno Tratorada Tam 37 | Origem: Minas do Leão ➔ Destino: Charqueadas. Peça reservada por 48 horas.",
                "time": "09:25",
                "type": "reservation_voucher",
                "payload": {
                    "res_id": "RES-8901",
                    "product_name": "Bota Coturno Couro Tratorada",
                    "size": "37",
                    "price": "R$ 289,90",
                    "pickup_store": "Charqueadas",
                    "source_store": "Minas do Leão",
                    "is_inter_store": True
                }
            },
            {
                "id": "MSG-7",
                "sender": "seller",
                "text": "Perfeito Mariana! Já reservei para você provar hoje.",
                "time": "09:42",
                "type": "text"
            }
        ]
    },
    {
        "id": "CHAT-102",
        "customer_id": "CUST-002",
        "customer_name": "Patrícia Vargas",
        "customer_phone": "(51) 98721-4355",
        "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=150&q=80",
        "assigned_seller": "Lucas Pereira",
        "seller_store": "Minas do Leão",
        "status": "in_progress",
        "unread": 1,
        "last_message": "Tem a Jaqueta Biker no tamanho G para eu buscar?",
        "last_time": "11:05",
        "messages": [
            {
                "id": "MSG-201",
                "sender": "customer",
                "text": "Oi Lucas! Vocês receberam reposição da jaqueta biker de couro sintético?",
                "time": "10:58",
                "type": "text"
            },
            {
                "id": "MSG-202",
                "sender": "customer",
                "text": "Tem a Jaqueta Biker no tamanho G para eu buscar?",
                "time": "11:05",
                "type": "text"
            }
        ]
    },
    {
        "id": "CHAT-103",
        "customer_id": "CUST-005",
        "customer_name": "Carla Mendonça",
        "customer_phone": "(51) 98112-9921",
        "avatar": "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=150&q=80",
        "assigned_seller": "Mariana Santos",
        "seller_store": "Charqueadas",
        "status": "open",
        "unread": 2,
        "last_message": "Gostaria de saber se tem a sandália salto bloco no 38 em Pantâno Grande.",
        "last_time": "11:45",
        "messages": [
            {
                "id": "MSG-301",
                "sender": "customer",
                "text": "Olá! Gostei muito da foto no stories das Lojas Lev.",
                "time": "11:40",
                "type": "text"
            },
            {
                "id": "MSG-302",
                "sender": "customer",
                "text": "Gostaria de saber se tem a sandália salto bloco no 38 em Pantâno Grande.",
                "time": "11:45",
                "type": "text"
            }
        ]
    },
    {
        "id": "CHAT-104",
        "customer_id": "CUST-004",
        "customer_name": "Beatriz Zimmermann",
        "customer_phone": "(51) 99312-7654",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80",
        "assigned_seller": "Fernanda Souza",
        "seller_store": "Encruzilhada do Sul",
        "status": "closed",
        "unread": 0,
        "last_message": "Adorei o vestido, serviu perfeitamente! Obrigada pelo atendimento rápido.",
        "last_time": "Ontem",
        "messages": [
            {
                "id": "MSG-401",
                "sender": "seller",
                "text": "Olá Beatriz! A sua reserva do vestido midi floral chegou na loja de Encruzilhada do Sul.",
                "time": "Ontem 14:10",
                "type": "text"
            },
            {
                "id": "MSG-402",
                "sender": "customer",
                "text": "Adorei o vestido, serviu perfeitamente! Obrigada pelo atendimento rápido.",
                "time": "Ontem 17:30",
                "type": "text"
            }
        ]
    }
]

# In-memory mirrors synced with SQLite
SELLERS: List[Dict[str, Any]] = []
CUSTOMERS: List[Dict[str, Any]] = []
PRODUCTS: List[Dict[str, Any]] = []
RESERVATIONS: List[Dict[str, Any]] = []
CHATS: List[Dict[str, Any]] = []


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(force_reset: bool = False) -> None:
    """Creates relational tables in SQLite and seeds initial Lojas Lev data if empty."""
    conn = get_connection()
    cur = conn.cursor()

    if force_reset:
        cur.executescript("""
            DROP TABLE IF EXISTS chat_messages;
            DROP TABLE IF EXISTS chats;
            DROP TABLE IF EXISTS reservations;
            DROP TABLE IF EXISTS product_stock;
            DROP TABLE IF EXISTS products;
            DROP TABLE IF EXISTS customers;
            DROP TABLE IF EXISTS sellers;
        """)

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS sellers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            store TEXT NOT NULL,
            role TEXT NOT NULL,
            avatar TEXT
        );

        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            city TEXT,
            preferred_store TEXT,
            avatar TEXT,
            shoe_size TEXT,
            clothing_size_top TEXT,
            clothing_size_bottom TEXT,
            favorite_brands_json TEXT,
            total_purchases INTEGER DEFAULT 0,
            lifetime_value REAL DEFAULT 0.0,
            vip_status INTEGER DEFAULT 0,
            notes TEXT,
            history_json TEXT
        );

        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            sku TEXT NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            brand TEXT NOT NULL,
            price REAL NOT NULL,
            image TEXT,
            description TEXT,
            type TEXT,
            sizes_json TEXT
        );

        CREATE TABLE IF NOT EXISTS product_stock (
            product_id TEXT NOT NULL,
            store TEXT NOT NULL,
            size TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (product_id, store, size),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE TABLE IF NOT EXISTS reservations (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            product_id TEXT NOT NULL,
            product_sku TEXT NOT NULL,
            product_name TEXT NOT NULL,
            product_image TEXT,
            size TEXT NOT NULL,
            price REAL NOT NULL,
            pickup_store TEXT NOT NULL,
            source_store TEXT NOT NULL,
            is_inter_store INTEGER NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            seller_name TEXT,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            avatar TEXT,
            assigned_seller TEXT,
            seller_store TEXT,
            status TEXT NOT NULL,
            unread INTEGER DEFAULT 0,
            last_message TEXT,
            last_time TEXT
        );

        CREATE TABLE IF NOT EXISTS chat_messages (
            id TEXT PRIMARY KEY,
            chat_id TEXT NOT NULL,
            seq INTEGER NOT NULL,
            sender TEXT NOT NULL,
            text TEXT NOT NULL,
            time TEXT NOT NULL,
            type TEXT DEFAULT 'text',
            payload_json TEXT,
            FOREIGN KEY (chat_id) REFERENCES chats(id)
        );
    """)

    # Seed if empty
    cur.execute("SELECT COUNT(*) as cnt FROM products")
    if cur.fetchone()["cnt"] == 0:
        for s in INITIAL_SELLERS:
            cur.execute(
                "INSERT INTO sellers (id, name, store, role, avatar) VALUES (?, ?, ?, ?, ?)",
                (s["id"], s["name"], s["store"], s["role"], s.get("avatar", ""))
            )

        for c in INITIAL_CUSTOMERS:
            cur.execute("""
                INSERT INTO customers (
                    id, name, phone, city, preferred_store, avatar,
                    shoe_size, clothing_size_top, clothing_size_bottom,
                    favorite_brands_json, total_purchases, lifetime_value,
                    vip_status, notes, history_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                c["id"], c["name"], c["phone"], c["city"], c["preferred_store"], c["avatar"],
                c["shoe_size"], c["clothing_size_top"], c["clothing_size_bottom"],
                json.dumps(c["favorite_brands"], ensure_ascii=False),
                c["total_purchases"], c["lifetime_value"],
                1 if c["vip_status"] else 0, c["notes"],
                json.dumps(c["history"], ensure_ascii=False)
            ))

        for p in INITIAL_PRODUCTS:
            cur.execute("""
                INSERT INTO products (
                    id, sku, name, category, brand, price, image, description, type, sizes_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                p["id"], p["sku"], p["name"], p["category"], p["brand"],
                p["price"], p["image"], p["description"], p["type"],
                json.dumps(p["sizes"], ensure_ascii=False)
            ))
            for store_name, sizes_dict in p["stock"].items():
                for sz, qty in sizes_dict.items():
                    cur.execute(
                        "INSERT INTO product_stock (product_id, store, size, quantity) VALUES (?, ?, ?, ?)",
                        (p["id"], store_name, sz, qty)
                    )

        for r in INITIAL_RESERVATIONS:
            cur.execute("""
                INSERT INTO reservations (
                    id, customer_id, customer_name, customer_phone,
                    product_id, product_sku, product_name, product_image,
                    size, price, pickup_store, source_store, is_inter_store,
                    status, created_at, expires_at, seller_name, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                r["id"], r["customer_id"], r["customer_name"], r["customer_phone"],
                r["product_id"], r["product_sku"], r["product_name"], r["product_image"],
                r["size"], r["price"], r["pickup_store"], r["source_store"],
                1 if r["is_inter_store"] else 0, r["status"],
                r["created_at"], r["expires_at"], r["seller_name"], r["notes"]
            ))

        for ch in INITIAL_CHATS:
            cur.execute("""
                INSERT INTO chats (
                    id, customer_id, customer_name, customer_phone, avatar,
                    assigned_seller, seller_store, status, unread, last_message, last_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ch["id"], ch["customer_id"], ch["customer_name"], ch["customer_phone"],
                ch["avatar"], ch["assigned_seller"], ch["seller_store"],
                ch["status"], ch["unread"], ch["last_message"], ch["last_time"]
            ))
            for idx, m in enumerate(ch["messages"]):
                cur.execute("""
                    INSERT INTO chat_messages (
                        id, chat_id, seq, sender, text, time, type, payload_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    m["id"], ch["id"], idx, m["sender"], m["text"], m["time"],
                    m.get("type", "text"),
                    json.dumps(m["payload"], ensure_ascii=False) if m.get("payload") else None
                ))

        conn.commit()

    conn.close()
    load_from_sqlite()


def load_from_sqlite() -> None:
    """Loads SQLite tables into the module-level lists."""
    global SELLERS, CUSTOMERS, PRODUCTS, RESERVATIONS, CHATS
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM sellers")
    SELLERS.clear()
    for row in cur.fetchall():
        SELLERS.append(dict(row))

    cur.execute("SELECT * FROM customers")
    CUSTOMERS.clear()
    for row in cur.fetchall():
        d = dict(row)
        CUSTOMERS.append({
            "id": d["id"],
            "name": d["name"],
            "phone": d["phone"],
            "city": d["city"],
            "preferred_store": d["preferred_store"],
            "avatar": d["avatar"],
            "shoe_size": d["shoe_size"],
            "clothing_size_top": d["clothing_size_top"],
            "clothing_size_bottom": d["clothing_size_bottom"],
            "favorite_brands": json.loads(d["favorite_brands_json"] or "[]"),
            "total_purchases": d["total_purchases"],
            "lifetime_value": d["lifetime_value"],
            "vip_status": bool(d["vip_status"]),
            "notes": d["notes"],
            "history": json.loads(d["history_json"] or "[]")
        })

    cur.execute("SELECT * FROM products")
    prod_rows = cur.fetchall()
    PRODUCTS.clear()
    for row in prod_rows:
        d = dict(row)
        cur.execute("SELECT store, size, quantity FROM product_stock WHERE product_id = ?", (d["id"],))
        stock_map: Dict[str, Dict[str, int]] = {st: {} for st in STORES}
        for srow in cur.fetchall():
            if srow["store"] not in stock_map:
                stock_map[srow["store"]] = {}
            stock_map[srow["store"]][srow["size"]] = srow["quantity"]

        PRODUCTS.append({
            "id": d["id"],
            "sku": d["sku"],
            "name": d["name"],
            "category": d["category"],
            "brand": d["brand"],
            "price": d["price"],
            "image": d["image"],
            "description": d["description"],
            "type": d["type"],
            "sizes": json.loads(d["sizes_json"] or "[]"),
            "stock": stock_map
        })

    cur.execute("SELECT * FROM reservations ORDER BY created_at DESC")
    RESERVATIONS.clear()
    for row in cur.fetchall():
        d = dict(row)
        d["is_inter_store"] = bool(d["is_inter_store"])
        RESERVATIONS.append(d)

    cur.execute("SELECT * FROM chats")
    chat_rows = cur.fetchall()
    CHATS.clear()
    for row in chat_rows:
        d = dict(row)
        cur.execute("SELECT * FROM chat_messages WHERE chat_id = ? ORDER BY seq ASC", (d["id"],))
        msgs = []
        for mrow in cur.fetchall():
            md = dict(mrow)
            msg_obj = {
                "id": md["id"],
                "sender": md["sender"],
                "text": md["text"],
                "time": md["time"],
                "type": md["type"]
            }
            if md["payload_json"]:
                msg_obj["payload"] = json.loads(md["payload_json"])
            msgs.append(msg_obj)
        d["messages"] = msgs
        CHATS.append(d)

    conn.close()


def save_state_to_sqlite() -> None:
    """Persists the current state of CUSTOMERS, PRODUCTS, RESERVATIONS, and CHATS into SQLite."""
    conn = get_connection()
    cur = conn.cursor()

    # Sync Customers
    for c in CUSTOMERS:
        cur.execute("""
            INSERT OR REPLACE INTO customers (
                id, name, phone, city, preferred_store, avatar,
                shoe_size, clothing_size_top, clothing_size_bottom,
                favorite_brands_json, total_purchases, lifetime_value,
                vip_status, notes, history_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            c["id"], c["name"], c["phone"], c.get("city", ""), c.get("preferred_store", "Charqueadas"),
            c.get("avatar", ""), c.get("shoe_size", ""), c.get("clothing_size_top", ""),
            c.get("clothing_size_bottom", ""),
            json.dumps(c.get("favorite_brands", []), ensure_ascii=False),
            c.get("total_purchases", 0), c.get("lifetime_value", 0.0),
            1 if c.get("vip_status") else 0, c.get("notes", ""),
            json.dumps(c.get("history", []), ensure_ascii=False)
        ))

    # Sync Product Stock
    for p in PRODUCTS:
        for store_name, sizes_dict in p["stock"].items():
            for sz, qty in sizes_dict.items():
                cur.execute("""
                    INSERT OR REPLACE INTO product_stock (product_id, store, size, quantity)
                    VALUES (?, ?, ?, ?)
                """, (p["id"], store_name, sz, qty))

    # Sync Reservations
    for r in RESERVATIONS:
        cur.execute("""
            INSERT OR REPLACE INTO reservations (
                id, customer_id, customer_name, customer_phone,
                product_id, product_sku, product_name, product_image,
                size, price, pickup_store, source_store, is_inter_store,
                status, created_at, expires_at, seller_name, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r["id"], r["customer_id"], r["customer_name"], r["customer_phone"],
            r["product_id"], r["product_sku"], r["product_name"], r.get("product_image", ""),
            r["size"], r["price"], r["pickup_store"], r["source_store"],
            1 if r["is_inter_store"] else 0, r["status"],
            r["created_at"], r["expires_at"], r.get("seller_name", "Mariana Santos"), r.get("notes", "")
        ))

    # Sync Chats & Messages
    for ch in CHATS:
        cur.execute("""
            INSERT OR REPLACE INTO chats (
                id, customer_id, customer_name, customer_phone, avatar,
                assigned_seller, seller_store, status, unread, last_message, last_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ch["id"], ch["customer_id"], ch["customer_name"], ch["customer_phone"],
            ch.get("avatar", ""), ch.get("assigned_seller", "Mariana Santos"),
            ch.get("seller_store", "Charqueadas"), ch["status"],
            ch.get("unread", 0), ch.get("last_message", ""), ch.get("last_time", "")
        ))
        cur.execute("DELETE FROM chat_messages WHERE chat_id = ?", (ch["id"],))
        for idx, m in enumerate(ch.get("messages", [])):
            cur.execute("""
                INSERT INTO chat_messages (
                    id, chat_id, seq, sender, text, time, type, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                m["id"], ch["id"], idx, m["sender"], m["text"], m["time"],
                m.get("type", "text"),
                json.dumps(m["payload"], ensure_ascii=False) if m.get("payload") else None
            ))

    conn.commit()
    conn.close()


def get_db_diagnostics() -> Dict[str, Any]:
    """Returns SQLite database metadata and row counts."""
    conn = get_connection()
    cur = conn.cursor()
    tables = ["sellers", "customers", "products", "product_stock", "reservations", "chats", "chat_messages"]
    counts = {}
    for t in tables:
        cur.execute(f"SELECT COUNT(*) as c FROM {t}")
        counts[t] = cur.fetchone()["c"]
    conn.close()
    size_kb = round(os.path.getsize(DB_PATH) / 1024, 1) if os.path.exists(DB_PATH) else 0
    return {
        "engine": "SQLite 3 (Relacional Persistente)",
        "database_file": "backend/levconnect.db",
        "size_kb": size_kb,
        "tables": counts
    }


# Initialize SQLite database automatically on import
init_db(force_reset=False)
