import streamlit as st
import math

st.set_page_config(page_title="Калькулятор Бани 2026", layout="wide")

st.title("🧖‍♂️ Профессиональный расчет: Парная + Печь + Полки")

# --- БЛОК 1: ПОМЕЩЕНИЕ ---
with st.sidebar:
    st.header("📏 Размеры парной")
    L = st.number_input("Глубина (мм)", value=2870)
    W = st.number_input("Ширина (мм)", value=3500)
    H = st.number_input("Высота (мм)", value=2600)
    
    st.divider()
    dist = st.number_input("Расстояние до объекта (км)", value=50)
    gsm_price = st.number_input("Цена бензина (руб/л)", value=65)

# --- БЛОК 2: ПОЛКИ (Новая логика) ---
st.header("🪵 Расчет полков")
num_levels = st.radio("Количество уровней полков", [1, 2, 3], horizontal=True)

levels_data = []
total_polki_len = 0

cols = st.columns(num_levels)
for i in range(num_levels):
    with cols[i]:
        st.subheader(f"Уровень {i+1}")
        l_len = st.number_input(f"Длина полка {i+1} (мм)", value=L, key=f"llen_{i}")
        l_width = st.number_input(f"Ширина полка {i+1} (мм)", value=800 if i==0 else 400, key=f"lwid_{i}")
        board_w = st.selectbox(f"Ширина доски", [95, 120, 140, 190], index=0, key=f"bw_{i}")
        gap = 5 # зазор между досками
        
        # Расчет количества досок на настил
        boards_count = math.ceil(l_width / (board_w + gap))
        
        # Торцевые доски (запрос пользователя)
        end_boards = st.selectbox("Торцевые доски (с торца)", [0, 1, 2], key=f"eb_{i}")
        
        total_boards = boards_count + end_boards
        st.info(f"Итого досок: {total_boards} шт.")
        levels_data.append({"len": l_len, "count": total_boards})

# --- БЛОК 3: ПЕЧЬ И ДЫМОХОД (Из ваших листов 07 и 08) ---
st.header("🔥 Печь и Дымоход")
col_p1, col_p2 = st.columns(2)

with col_p1:
    stove_type = st.selectbox("Тиp печи", ["Дровяная (сталь)", "Дровяная (чугун)", "Электрическая", "Газовая"])
    has_portal = st.checkbox("Нужен кирпичный портал?")
    has_stones = st.checkbox("Камни для печи (с укладкой)")
    has_fence = st.checkbox("Ограждение печи")

with col_p2:
    has_chimney = st.toggle("Включить дымоход в расчет")
    if has_chimney:
        chimney_type = st.radio("Класс дымохода", ["Эконом", "Стандарт", "Премиум"])
        chimney_len = st.number_input("Высота дымохода (м)", value=4.0)

# --- БЛОК 4: РАБОТЫ (Автоматизация на основе выбора) ---
st.header("🛠 Список работ")

base_works = [
    {"name": "Монтаж каркаса и вагонки", "price": 1650, "unit": "м2", "val": (2*(L+W)*H + L*W)/1000000},
    {"name": "Монтаж полков", "price": 35000, "unit": "компл", "val": 1},
]

if has_portal:
    base_works.append({"name": "Изготовление портала печи", "price": 18000, "unit": "шт", "val": 1})
if has_stones:
    base_works.append({"name": "Отмывка и укладка камней", "price": 1500, "unit": "шт", "val": 1})
if has_chimney:
    base_works.append({"name": "Монтаж дымохода", "price": 15000, "unit": "шт", "val": 1})

work_df = pd.DataFrame(base_works)
work_df['Итого'] = work_df['price'] * work_df['val']
st.table(work_df[['name', 'val', 'unit', 'price', 'Итого']])

# --- ИТОГО ---
total_sum = work_df['Итого'].sum()
st.sidebar.metric("ОБЩАЯ СМЕТА", f"{total_sum:,.0f} руб.")

if st.button("📥 Сформировать отчет для WhatsApp"):
    report = f"Заказ: {L}x{W}x{H}\n"
    report += f"Полки: {num_levels} уровня\n"
    report += f"Печь: {stove_type}\n"
    report += f"ИТОГО: {total_sum:,.0f} руб."
    st.text_area("Скопируйте этот текст:", report)
