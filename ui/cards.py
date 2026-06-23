import streamlit as st


def metric_card(col, titulo, valor, delta=None):
    with col:
        delta_html = ""

        if delta is not None:
            delta_html = f"""
            <div class="runatics-metric-delta">
                {delta}
            </div>
            """

        st.markdown(
            f"""
            <div class="runatics-metric-card">
                <div class="runatics-metric-title">
                    {titulo}
                </div>
                <div class="runatics-metric-value">
                    {valor}
                </div>
                {delta_html}
            </div>
            """,
            unsafe_allow_html=True,
        )


def info_card(titulo, contenido):
    st.markdown(
        f"""
        <div class="runatics-card">
            <h4>{titulo}</h4>
            <p>{contenido}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
