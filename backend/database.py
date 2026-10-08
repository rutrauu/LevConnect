"""
LevConnect - In-Memory Database & State Management
Case Study: Lojas Lev (Minas do Leão, Charqueadas, Encruzilhada do Sul, Pantâno Grande, Rio Pardo)
"""

from datetime import datetime, timedelta
import random

STORES = [
    "Charqueadas",
    "Minas do Leão",
    "Encruzilhada do Sul",
    "Pantâno Grande",
    "Rio Pardo"
]

SELLERS = [
    {"id": "SEL-01", "name": "Mariana Santos", "store": "Charqueadas", "role": "Vendedora Digital"},
    {"id": "SEL-02", "name": "Lucas Pereira", "store": "Minas do Leão", "role": "Vendedor Balcão & Whats"},
    {"id": "SEL-03", "name": "Camila Oliveira", "store": "Rio Pardo", "role": "Gerente de Atendimento"},
    {"id": "SEL-04", "name": "Rodrigo Silva", "store": "Pantâno Grande", "role": "Vendedor"},
    {"id": "SEL-05", "name": "Fernanda Souza", "store": "Encruzilhada do Sul", "role": "Vendedora"}
]

CUSTOMERS = [
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
        "shoe_size": "41",
        "clothing_size_top": "GG",
        "clothing_size_bottom": "44",
        "favorite_brands": ["Lev Man", "Reserva", "Osklen"],
        "total_purchases": 3,
        "lifetime_value": 890.00,
        "vip_status": False,
        "notes": "Costuma comprar presentes para a esposa e calçados casuais para si.",
        "history": [
            {"date": "2026-09-01", "item": "Tênis Casual Couro (41)", "price": 259.90, "store": "Rio Pardo"}
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

PRODUCTS = [
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

RESERVATIONS = [
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

CHATS = [
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
                    "source_store": "Minas do Leão"
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
