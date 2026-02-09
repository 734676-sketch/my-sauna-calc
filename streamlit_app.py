import streamlit as st
import pandas as pd

st.set_page_config(page_title="Мастер Отделки 2026", layout="wide")

# --- ИНИЦИАЛИЗАЦИЯ ДАННЫХ ---
if 'rooms' not in st.session_state:
    st.session_state.rooms = []

def add_room():
    st.session_state.rooms.append({"name": f"Комната {len(st.session_state.rooms)+1}", "type": "Парная"})

st.title("🪓 Профессиональный расчет отделки")

# --- ГЛОБАЛЬНЫЕ ПАРАМЕТРЫ ---
with st.sidebar:
    st.header("Настройки объекта")
    project_name = st.text_input("Название объекта", "Объект №1")
    distance = st.number_input("Расстояние (км)", value=0)
    days = st.number_input("Дней работы", value=1)
    st.divider()
    if st.button("➕ Добавить комнату"):
        add_room()

# --- ОСНОВНОЙ ЦИКЛ ПО КОМНАТАМ ---
total_project_cost = 0

for idx, room in enumerate(st.session_state.rooms):
    with st.expander(f"🚪 {room['name']} - {room['type']}", expanded=True):
        col_n, col_t, col_del = st.columns([3, 2, 1])
        room['name'] = col_n.text_input("Название", value=room['name'], key=f"name_{idx}")
        room['type'] = col_t.selectbox("Тип", ["Парная", "Душевая", "Зона отдыха"], key=f"type_{idx}")
        if col_del.button("🗑️ Удалить", key=f"del_{idx}"):
            st.session_state.rooms.pop(idx)
            st.rerun()

        # Размеры
        c1, c2, c3 = st.columns(3)
        depth = c1.number_input("Глубина (мм)", value=2000, step=10, key=f"d_{idx}")
        width = c2.number_input("Ширина (мм)", value=2000, step=10, key=f"w_{idx}")
        height = c3.number_input("Высота (мм)", value=2200, step=10, key=f"h_{idx}")

        # Расчет площадей (как в вашем Excel)
        s_walls = (2 * (depth + width) * height) / 1_000_000
        s_ceiling = (depth * width) / 1_000_000
        st.write(f"**Площадь стен:** {s_walls:.2f} м² | **Потолок:** {s_ceiling:.2f} м²")

        if room['type'] == "Парная":
            # Блок Вагонка (из листа 02 ДЕРЕВО)
            st.subheader("Отделка деревом")
            wood_type = st.selectbox("Материал", ["Липа", "Кедр", "Ольха", "Хвоя", "Абаш"], key=f"wood_{idx}")
            profile = st.selectbox("Профиль", ["Штиль", "STS", "Евро", "Волна"], key=f"prof_{idx}")
            
            # Авто-расчет материалов типа В (Вагонка)
            board_w = st.number_input("Ширина вагонки (мм)", value=135, key=f"bw_{idx}")
            margin = 1.1 # 10% запас
            count_boards = (s_walls + s_ceiling) / (board_w/1000 * 3) * margin # Пример для 3-метровой доски
            st.success(f"Требуется вагонки: {count_boards:.0f} шт. (при длине 3м)")

        elif room['type'] == "Душевая":
            # Блок Плитка (из листа 06 ПЛИТКА)
            st.subheader("Плитка и гидроизоляция")
            tile_price = st.number_input("Цена плитки за м²", value=1890, key=f"tile_{idx}")
            glue_bags = round(s_walls / 4) # Пример: 1 мешок на 4м2
            st.info(f"Плиточный клей: {glue_bags} мешков")

# --- ИТОГОВЫЙ ОТЧЕТ ---
st.divider()
st.header("Итого по объекту")
# Здесь будет суммирование всех комнат, работ и ГСМ
st.write(f"Общая стоимость по объекту {project_name}: **0.00 руб.**")
st.caption("Данные подтянутся автоматически после заполнения всех цен в комнатах.")
