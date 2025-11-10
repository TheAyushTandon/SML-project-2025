user_base = st.text_input("Type something memorable (e.g. a name, hobby, phrase):")
if st.button("Generate a strong password"):
    from src.generator.password_generator import generate_password
    result = generate_password(user_base)
    st.write("**Suggestions:**")
    for p in result["suggestions"]:
        st.code(p)
    st.success(f"✅ Best choice: {result['best_password']}")
