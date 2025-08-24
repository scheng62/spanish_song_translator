import streamlit as st
import pandas as pd

# st.set_page_config(
#     page_title="Vocabulary Notes",
#     page_icon="📖"
# )

### Need to append on previous vocabulary list

def vocab_main():
    st.markdown("# Vocabulary Builder 📖")
    # st.sidebar.markdown("# Vocabulary Builder 📖")

    st.session_state.clear_vocab = False

    if not st.session_state.tutor_notes:
        st.info("No new vocabularies yet. Go to the Translator page first.")
    else:
        df = pd.DataFrame(st.session_state.tutor_notes)

        # Check if the clear button has been fired or not
        if st.button("Clear Vocabulary", type='primary'):
            st.session_state.clear_vocab = True

        if st.session_state.clear_vocab == False:
            st.dataframe(
                df,
                column_config={
                    "Conjugations": st.column_config.TextColumn(
                        "Conjugations",
                        width="large",
                        max_chars=None   
                    )
                },
                use_container_width=True
                
            )
        else:
            st.info("No new vocabularies yet. Go to the Translator page first.")
    
    # if st.button("Clear Vocabulary", type='primary'):
    #     st.session_state.tutor_notes = None
    #     st.info("No new vocabularies yet. Go to the Translator page first.")


if __name__ == "__main__":
    vocab_main()