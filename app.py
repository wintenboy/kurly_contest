import os
import re
import json
import base64
import requests
import pandas as pd
import networkx as nx
from PIL import Image
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory
from htmlTemplates import css, bot_template, user_template
from streamlit_agraph import agraph, Node, Edge, Config, TripleStore
from langchain_experimental.agents.agent_toolkits.pandas.base import create_pandas_dataframe_agent


@st.cache_data
def load_data(csv_file_path):
    df = pd.read_csv(csv_file_path, encoding='utf-8')
    return df

def main():

    config = Config(
    width=750,  # 그래프를 그릴 캔버스 사이즈
    height=950,  # 그래프를 그릴 캔버스 사이즈
    directed=False,  # directed or undirected graph 를 그릴 수 있다.
    physics=True,   # 그래프 랜더링 후 node 의 움직임을 허용할 것인지
    hierarchical=False,  # 그래프가 tree 구조인 경우
  nodeHighlightBehavior=True,  # node highlight
    highlightColor='#F7A7A6',
    collapsible=True,
    staticGraphWithDragAndDrop=False,
    link={'labelProperty': 'label', 'renderLabel': True},
    staticGraph=False
    )
    

    st.set_page_config(page_title="그래프")
    st.write(css, unsafe_allow_html=True)

    main_container = st.container()
    sidebar_container = st.sidebar.container()
    with sidebar_container:
        top_image = Image.open('trippyPattern.png')
        st.image(top_image)
        uploaded_file = st.file_uploader("Generating Knowledge Graph . . .")

    with main_container:
        st.title("CHAT WITH KNOWLEDGE GRAPH")
        if uploaded_file is not None:
            with st.spinner("🔥🔥🔥🔥분석 중🔥🔥🔥🔥"):
                df = load_data(uploaded_file)
                df.dropna(axis=0, inplace=True)
                df.drop(df[df['weight'] < 30].index, axis=0,inplace=True)
                # Prepare nodes and edges for agraph
                nodes = set()
                edges = []

                for index, row in df.iterrows():
                    from_node = row['from']
                    to_node = row['to']
                    weight = row['weight']

                    nodes.add(from_node)
                    nodes.add(to_node)

                    edges.append(Edge(source=from_node, target=to_node, label=str(weight)))

                # Convert set of nodes to list of Node objects
                node_list = [Node(id=node, label=node) for node in nodes]

                # Render the graph in Streamlit
                
                agraph(nodes=node_list, edges=edges, config={'height': 700 , 
                                                            'width': 950, 
                                                            'directed': False,
                                                            'physics': True,
                                                            'hierarchical':False,
                                                            'collapsible':True,
                                                            
                                                            })
        
            context = st.text_area(label='Additional Context', height=100)
            if st.button('질문하기'):
                with st.spinner('대답 중') :

                    agent = create_pandas_dataframe_agent(ChatOpenAI(temperature=0,
                                                        model='gpt-4'),
                                                        df=df,
                                                        verbose=True,
                                                        agent_type = AgentType.OPENAI_FUNCTIONS)
                    output = agent.run(f'데이터 설명 : 이 데이터는 지식 그래프 시각화를 위해 만들어진 데이터입니다.변수 설명 : "from"은 블로그 포스팅의 주요 키워드를 의미하고, "to"는 hashtags를 의미합니다. "weight"는 중요도를 의미합니다. 다음의 질문에 대답하세요.{context}')
                    st.markdown(bot_template.replace("{{MSG}}", output), unsafe_allow_html=True)


if __name__ == "__main__":
    
    load_dotenv()
    main()