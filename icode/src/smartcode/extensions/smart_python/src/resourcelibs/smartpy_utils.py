DESCRIPTION = """
    <ul>
        <li>Tree, Doctor</li>
        <li>Warnings, Analyzes</li>
        <li>Debug, Tests</li>
        <li>Refactor</li>
    </ul>
"""
SERVER_NAME = "smartpy_language_server"

deep_analyze_doc = """
            <small>
                Get advanced diagnosis for your code,
                get data such as:
                <ul>
                    <li>Cyclomatic Complexity</li>
                    <li>Maintainability Index</li>
                </ul>
                <p>
                    click 
                    <strong>
                        <a href="www.github.io">here</a>
                    </strong>
                    to learn more
                    <strong>
                    or
                    </strong>
                </p>
            </small>
        """
code_warnings_doc = """
            <small>
                Get warnings for your code,
                problems related to pep8 in
                your code will be detected and
                presented here, with the option
                to fix some of them!
                to use this functionality click
                on get warnings, here or on icode labs
                <p>
                    click 
                    <strong>
                        <a href="www.github.io">here</a>
                    </strong>
                    to learn more
                    <strong>
                    or
                    </strong>
                </p>
            </small>
        """
code_doctor_doc = """
            <small>
                Get basic diagnosis for your code,
                get data such as:
                <ul>
                    <li>number of lines</li>
                    <li>coments</li>
                    <li>logic lines of code</li>
                    <li>blank lines</li>
                    <li>syntax errors and more.</li>
                </ul>
                <p>
                    click 
                    <strong>
                        <a href="www.github.io">here</a>
                    </strong>
                    to learn more
                    <strong>
                    or
                    </strong>
                </p>
            </small>
        """

def format_analyze_rank(rank:str):
    if rank == "A":
        return (f"<h2 style='color:#9de35f'>{rank}</h2>", "<strong style='color:#9de35f'>low risk - simple block</strong>")
    elif rank == "B":
        return (f"<h2 style='color:#c9e35f'>{rank}</h2>", "<strong style='color:#c9e35f'>low risk - well structured and stable block</strong>")
    elif rank == "C":
        return (f"<h2 style='color:#e3df5f'>{rank}</h2>", "<strong style='color:#e3df5f'>moderate risk - slightly complex block</strong>")
    elif rank == "D":
        return (f"<h2 style='color:#e3b05f'>{rank}</h2>", "<strong style='color:#e3b05f'>more than moderate risk - more complex block</strong>")
    elif rank == "E":
        return (f"<h2 style='color:#e37e5f'>{rank}</h2>", "<strong style='color:#e37e5f'>high risk - complex block, alarming</strong>")
    elif rank == "F":
        return (f"<h2 style='color:#e35f5f'>{rank}</h2>", "<strong style='color:#e35f5f'>very high risk - error-prone, unstable block</strong>")
    else:
        return (f"<h2>{rank}</h2>", "")