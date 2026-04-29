"""Add save button to sidebar"""
import streamlit as st
import json
import os

def add_save_button(module_name):
    st.sidebar.markdown("### Save Progress")
    if st.sidebar.button("Save Current State", key=f"save_{module_name}"):
        save_file = f"users/{st.session_state.username}/pipeline_state.json"
        os.makedirs(f"users/{st.session_state.username}", exist_ok=True)
        state = {
            "current_module": module_name,
            "run_name": st.session_state.get("run_name"),
            "certified_k_dwarfs": list(st.session_state.get("certified_k_dwarfs", [])),
            "target_ids": list(st.session_state.get("target_ids", [])),
        }
        with open(save_file, "w") as f:
            json.dump(state, f, indent=2, default=str)
        st.sidebar.success("Progress saved!")
