import streamlit as st
import pandas as pd
import numpy as np
import time


st.write("testing")

st.text("what is this")

df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})

df

st.write("Here's our first attempt at using data to create a table:")
st.write(pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
}))
st.write("Try a new table")


st.table(pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
}))

st.dataframe(pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
}))


df1 = np.random.rand(10, 20)
st.dataframe(df1)


df2 = pd.DataFrame(np.random.randn(10, 20), columns = ('col %d' % i for i in range(20)))

st.dataframe(df2.style.highlight_max(axis=1))


chart_data = pd.DataFrame(np.random.randn(20, 3), columns=['a', 'b', 'c'])
st.line_chart(chart_data)
st.dataframe(chart_data)

map_data = pd.DataFrame(np.random.randn(1000,2)/[50, 50]+[37.76, -122.4], columns=['lat', 'lon'])
st.map(map_data)


x = st.slider('x')
st.write(x, 'squared is', x*x)

x = st.selectbox('x', [1, 2, 3, 4])


st.text_input("Your fav artist", key="name")

st.session_state.name

if st.checkbox('show dataframe'):
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=['a', 'b', 'c'])
    chart_data
    st.write('is this gonna be shown')



df = pd.DataFrame({'first column': [1, 2, 3, 4], 'second column': [10, 20, 30, 40]})
optin = st.selectbox("Which number do you like the best", df['first column'])

'You selected: ', optin



add_selectbox = st.sidebar.selectbox("How would you like to be contacted?", ['Email', 'Home Phone'])

add_slider = st.sidebar.slider('Select a range of values', 0.0, 100.0, (25.0, 75.0))


left_column, right_column = st.columns(2)
left_column.button('Press me!')


with right_column:
    chosen = st.radio('Sorting hat', ("Gryffindor", "Ravenclaw", "Hufflepuff", "Slytherin"))
    # st.write(f"you are in {chosen} house")

'starting a long computation...'

latest_iteration = st.empty()
bar = st.progress(0)

for i in range(100):
    latest_iteration.text(f'Iteration {i+1}')
    bar.progress(i+1)
    time.sleep(0.1)

'... and now we\'re done!'



# Define the pages
main_page = st.Page("main.py", title="Main Page", icon="🎈")
page_1 = st.Page("page1.py", title="Page 1", icon="❄️")
page_2 = st.Page("page2.py", title="Page 2", icon="🎉")

# Set up navigation
pg = st.navigation([main_page, page_1, page_2])

# Run the selected page
pg.run()