import os

from model_client import generate_response


def load_text_file(file_path):
   
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def main():
    
    task = input("Choose a task (summarization/extraction/classification): ").strip().lower()
    sample_type = input("Choose sample (normal/long/ambiguous/incomplete): ").strip().lower()

    # Build file paths
    prompt_path = os.path.join(
        "prompts_templates",
        f"{task}_prompt.md"
    )

    sample_path = os.path.join(
        "sample_texts",
        task,
        f"{sample_type}.txt"
    )

    # Check if files exist
    if not os.path.exists(prompt_path):
        print(f"Error: Prompt file not found -> {prompt_path}")
        return

    if not os.path.exists(sample_path):
        print(f"Error: Sample file not found -> {sample_path}")
        return

    # Load files
    prompt_template = load_text_file(prompt_path)
    sample_text = load_text_file(sample_path)

    # Replace placeholder with sample text
    final_prompt = prompt_template.replace("{text}", sample_text)

    # Send prompt to model
    result = generate_response(final_prompt)

    # Display result
    print("\n" + "=" * 60)
    print("MODEL RESPONSE")
    print("=" * 60)
    print(result["text"])

    print("\n" + "=" * 60)
    print(f"Model    : {result['model']}")
    print(f"Latency  : {result['latency']:.2f} seconds")
    print("=" * 60)

    # Save output
    os.makedirs("outputs", exist_ok=True)

    output_file = os.path.join(
        "outputs",
        f"{task}_{sample_type}_output.txt"
    )

    with open(output_file, "w", encoding="utf-8") as file:
        file.write("=== MODEL RESPONSE ===\n\n")
        file.write(result["text"])
        file.write("\n\n")
        file.write(f"Model: {result['model']}\n")
        file.write(f"Latency: {result['latency']:.2f} seconds\n")

    print(f"\nOutput saved to: {output_file}")


if __name__ == "__main__":
    main()