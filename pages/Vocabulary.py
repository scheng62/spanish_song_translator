import streamlit as st
import pandas as pd

# st.set_page_config(
#     page_title="Vocabulary Notes",
#     page_icon="📖"
# )


def vocab_main():
    st.markdown("# Vocabulary Builder 📖")
    # st.sidebar.markdown("# Vocabulary Builder 📖")

    if "tutor_notes" not in st.session_state or not st.session_state.tutor_notes:
        st.info("No new vocabularies yet. Go to the Translator page first.")
    else:
        df = pd.DataFrame(st.session_state.tutor_notes)
        st.dataframe(df)


if __name__ == "__main__":
    vocab_main()