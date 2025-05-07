import streamlit as st
import requests
import json

def run_frontend():
    st.title("Task Manager")
    token = st.session_state.get("token", None)

    if not token:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                try:
                    response = requests.post(
                        "http://localhost:8000/login",
                        json={"username": username, "password": password}
                    )
                    if response.status_code == 200:
                        st.session_state["token"] = response.json()["token"]
                        st.success("Logged in!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        with tab2:
            st.subheader("Register")
            reg_username = st.text_input("Username", key="reg_username")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            if st.button("Register"):
                try:
                    response = requests.post(
                        "http://localhost:8000/register",
                        json={"username": reg_username, "password": reg_password}
                    )
                    if response.status_code == 200:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(response.json().get("detail", "Registration failed"))
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.subheader("Tasks")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Display tasks
        try:
            response = requests.get("http://localhost:8000/tasks", headers=headers)
            if response.status_code == 200:
                tasks = response.json()
                for task in tasks:
                    st.write(f"{task['title']} - {task['status']} (Priority: {task['priority']})")
                    with st.form(f"update_task_{task['id']}"):
                        new_status = st.selectbox("Status", ["pending", "in_progress", "completed"], key=f"status_{task['id']}")
                        if st.form_submit_button("Update"):
                            update_response = requests.put(
                                f"http://localhost:8000/tasks/{task['id']}",
                                json={"status": new_status},
                                headers=headers,
                            )
                            if update_response.status_code == 200:
                                st.success("Task updated!")
                                st.rerun()
            else:
                st.error("Failed to load tasks")
        except Exception as e:
            st.error(f"Error loading tasks: {str(e)}")

        # Create task
        with st.form("new_task"):
            title = st.text_input("Title")
            description = st.text_area("Description")
            priority = st.number_input("Priority", min_value=0, max_value=10)
            if st.form_submit_button("Add Task"):
                try:
                    response = requests.post(
                        "http://localhost:8000/tasks",
                        json={"title": title, "description": description, "priority": priority},
                        headers=headers,
                    )
                    if response.status_code == 200:
                        st.success("Task added!")
                        st.rerun()
                    else:
                        st.error(f"Failed to add task: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        # Logout
        if st.button("Logout"):
            st.session_state.pop("token")
            st.success("Logged out!")
            st.rerun()

if __name__ == "__main__":
    run_frontend()