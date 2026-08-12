from tools.nodes import (
    error_analyzer,
    fix_generator,
    teaching_loop,
    concept_explainer,
    tradeoff_analyst,
    test_writer
)

state = {
    "broken_code": "print(x)",
    "error_message": "NameError: name 'x' is not defined"
}


def run_pipeline():
    s = state.copy()

    print("\n🔹 Step 1: Error Analyzer")
    s.update(error_analyzer(s))
    print(s)

    print("\n🔹 Step 2: Fix Generator")
    s.update(fix_generator(s))
    print(s)

    print("\n🔹 Step 3: Teaching Loop")
    s.update(teaching_loop(s))
    print(s)

    print("\n🔹 Step 4: Concept Explainer")
    s.update(concept_explainer(s))
    print(s)

    print("\n🔹 Step 5: Tradeoff Analyst")
    s.update(tradeoff_analyst(s))
    print(s)

    print("\n🔹 Step 6: Test Writer")
    s.update(test_writer(s))
    print(s)

    print("\n✅ FINAL OUTPUT:\n", s)


if __name__ == "__main__":
    run_pipeline()