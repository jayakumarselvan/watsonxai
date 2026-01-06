from ibm_watsonx_orchestrate.agent_builder.tools import tool


@tool
def hello_word(name: str):
    """
    This function will greet the user

    :param name: Name of the user
    :returns: Greet message
    """
    return f"Hello, {name}"


if __name__ == "__main__":
    print(hello_word("Wxo"))
