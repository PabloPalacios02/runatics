import streamlit as st


def aplicar_estilos():
    st.markdown(
        """
        <style>
        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        header {
            visibility: hidden;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #020617 0%, #0f172a 45%, #111827 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        section[data-testid="stSidebar"] * {
            color: #f8fafc !important;
        }

        section[data-testid="stSidebar"] button {
            border-radius: 14px !important;
            border: 1px solid rgba(255,255,255,0.18) !important;
        }

        .stButton > button {
            border-radius: 14px;
            border: 1px solid #dbeafe;
            background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
            color: white;
            font-weight: 700;
            padding: 0.55rem 1rem;
            transition: 0.15s ease-in-out;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 18px rgba(37, 99, 235, 0.25);
            color: white;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }

        .stTabs [data-baseweb="tab"] {
            background: #f8fafc;
            border-radius: 999px;
            padding: 0.55rem 1rem;
            border: 1px solid #e5e7eb;

            color: #000000 !important;
            font-weight: 700 !important;
        }

        .stTabs [data-baseweb="tab"] * {
            color: #000000 !important;
            font-weight: 700 !important;
        }

        .stTabs [aria-selected="true"] {
            background: #dbeafe !important;
            border: 2px solid #2563eb !important;
        }

        .stTabs [aria-selected="true"] * {
            color: #1d4ed8 !important;
            font-weight: 800 !important;
        }

        div[data-testid="stDataFrame"] {
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid #e5e7eb;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
        }

        .runatics-hero {
            background:
                radial-gradient(circle at top left, rgba(255,255,255,0.25), transparent 30%),
                linear-gradient(135deg, #0ea5e9 0%, #2563eb 45%, #7c3aed 100%);
            color: white;
            padding: 1.8rem 2rem;
            border-radius: 28px;
            margin-bottom: 1.5rem;
            box-shadow: 0 18px 40px rgba(37, 99, 235, 0.22);
        }

        .runatics-hero h1 {
            color: white;
            margin-bottom: 0.3rem;
            font-size: 2.2rem;
            font-weight: 900;
            letter-spacing: -0.03em;
        }

        .runatics-hero p {
            color: rgba(255,255,255,0.9);
            font-size: 1rem;
            margin: 0;
        }

        .runatics-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 22px;
            padding: 1.2rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.07);
            margin-bottom: 1rem;
        }

        .runatics-muted {
            color: #64748b;
            font-size: 0.95rem;
        }
        
        .runatics-metric-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 22px;
            padding: 1.2rem 1.4rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.07);
            min-height: 125px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .runatics-metric-title {
            color: #000000 !important;
            font-size: 1rem;
            font-weight: 800;
            margin-bottom: 0.45rem;
        }

        .runatics-metric-value {
            color: #0f172a !important;
            font-size: 2rem;
            font-weight: 900;
            line-height: 1.1;
        }

        .runatics-metric-delta {
            margin-top: 0.45rem;
            color: #16a34a;
            font-size: 0.9rem;
            font-weight: 700;
        }

        @media (max-width: 768px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1rem;
            }

            .runatics-hero {
                padding: 1.3rem;
                border-radius: 22px;
            }

            .runatics-hero h1 {
                font-size: 1.65rem;
            }

            div[data-testid="stMetricValue"] {
                font-size: 1.35rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(titulo, subtitulo):
    st.markdown(
        f"""
        <div class="runatics-hero">
            <h1>{titulo}</h1>
            <p>{subtitulo}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card_html(contenido):
    st.markdown(
        f"""
        <div class="runatics-card">
            {contenido}
        </div>
        """,
        unsafe_allow_html=True,
    )
