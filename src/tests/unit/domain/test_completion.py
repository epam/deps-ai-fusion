from deps_ai_fusion.domain.model.conversation import Completion, Conversation


def test_completion__creation__default_values_passed(conversation: Conversation) -> None:
    something, some_confidence = "something", 0.25
    created_completion = conversation.add_completion(
        provider=something,
        model=something,
        question=something,
        response=something,
        confidence=some_confidence,
    )

    assert created_completion.llm_reference.provider == something
    assert created_completion.llm_reference.model == something
    assert created_completion.question == something
    assert created_completion.response == something
    assert created_completion.confidence == some_confidence

    assert created_completion.code
    assert created_completion.created_at


def test_completion__dumping(test_completion: Completion) -> None:
    assert test_completion.dump() == {
        "question": test_completion.question,
        "response": test_completion.response,
    }
