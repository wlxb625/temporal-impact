"""Local Streamlit UI for the deterministic false-death scenario."""

import streamlit as st

from temporal_impact import ImpactEngine
from temporal_impact.demo.scenario import false_death_event, load_story

st.set_page_config(page_title="Temporal Impact Demo", layout="wide")
st.title("Temporal Impact · 师父假死演示")

if "engine" not in st.session_state:
    st.session_state.engine = ImpactEngine(database_url="sqlite://")
    st.session_state.report = None
engine: ImpactEngine = st.session_state.engine

first, second, third = st.columns(3)
if first.button("加载演示"):
    load_story(engine)
    st.success("已加载师父死亡设定与依赖图。")
if second.button("应用：师父假死"):
    load_story(engine)
    st.session_state.report = engine.analyze(false_death_event())
    st.success("变更已分析；未写回任何宿主系统。")
if third.button("重置"):
    st.session_state.engine = ImpactEngine(database_url="sqlite://")
    st.session_state.report = None
    st.rerun()

tabs = st.tabs(
    ["Overview", "Event Timeline", "Shadow Graph", "Impact Report", "Observations", "Proposals"]
)
with tabs[0]:
    st.metric("第12章 conflict_score", "0.94", "0.82")
    st.metric("第20章 staleness_score", "0.86", "0.78")
    st.metric("整体 stability_score", "0.51", "-0.33")
with tabs[1]:
    st.json(false_death_event().model_dump(mode="json"))
with tabs[2]:
    st.json(engine.graph_data("novel-demo"))
with tabs[3]:
    st.json(st.session_state.report.model_dump(mode="json") if st.session_state.report else {})
with tabs[4]:
    observations = engine.repository.get_observations("novel-demo")
    st.json([item.model_dump(mode="json") for item in observations])
with tabs[5]:
    st.json([item.model_dump(mode="json") for item in engine.list_proposals("novel-demo")])
