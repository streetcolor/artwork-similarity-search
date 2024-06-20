import streamlit as st
import io
from qdrant.vector_searcher import VectorSearch
from config import QDRANT_URL, QDRANT_KEY, EMBEDDER, COLLECTION_NAME, IMAGES_DIR
from PIL import Image
import requests
st.set_page_config(
    page_title="Artwork Search", layout="centered", page_icon="./images/icon.png"
)


@st.cache_resource(show_spinner=False)
def load_search_object():
    return VectorSearch(encoder_name=EMBEDDER, qdrant_url=QDRANT_URL,
                            qdrant_key=QDRANT_KEY, collection_name=COLLECTION_NAME)

vectorsearch = load_search_object()

st.sidebar.image("images/header_sidebar.png")
st.sidebar.title("Vector Search Engine")
st.sidebar.caption("Easily find similar artworks.")


st.sidebar.markdown("This app uses the CLIP model to encode images and stores the embeddings in a vector database called [Qdrant](https://qdrant.tech/). Check out their documentation [here](https://qdrant.tech/documentation/), ", unsafe_allow_html=True)


st.sidebar.markdown("Source code can be found [here]( https://github.com/Otman404/artwork-similarity-search)")
st.sidebar.markdown("Made by [Otmane Boughaba](https://www.linkedin.com/in/otmaneboughaba/)")


st.image("images/header.png")
search_option = st.selectbox(
    'How would you like to search for similar artworks?',
    ('Image search', 'Text search'))


image_bytes = None
artwork_desc = ""

if search_option == 'Image search':
    st.markdown('### Search for artworks similar to the uploaded image.')
    uploaded_file = st.file_uploader("Upload image", type=[
                                     "png", "jpeg", "jpg"], accept_multiple_files=False, key=None, help="upload image")
    if uploaded_file:
        # To read file as bytes
        image_bytes = uploaded_file.getvalue()
        st.image(image_bytes, width=400)
else:
    artwork_desc = st.text_input("Describe the artwork")

if image_bytes or artwork_desc:

    k = st.slider(label='Choose how many similar images to get',
                  min_value=1, max_value=10, step=1, value=3)

    if st.button('Search'):

        if not image_bytes and not artwork_desc:
            st.write("error")

        elif image_bytes:
            with st.spinner('Searching the vector database for similar artworks'):
                search_result = vectorsearch.search(
                    Image.open(io.BytesIO(image_bytes)), k)
        elif artwork_desc:
            with st.spinner("Searching for atwork that matches your description..."):
                search_result = vectorsearch.search(artwork_desc, k)

        
        st.title("Image search result")
        for id, r in enumerate(search_result):
            st.subheader(f"{r['artist']} |{id} ")
            st.write(id)
            st.markdown(
                f"[*Learn more*]({id})")

            url = "https://media.artsper.com/artwork/{id}_1_m.jpg".format(id=r['image_name'].split('_')[-1].split('.')[0])

            image = Image.open(requests.get(url, stream=True).raw).resize((400, 400), Image.LANCZOS)
            st.image(image)

            st.divider()