"""
Generator module for LLM-based answer generation.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import os
from loguru import logger


class PromptLoader:
    """
    Loads and manages markdown prompt files.
    """

    def __init__(
        self,
        prompts_dir: str,
        system_prefix: str = "system_",
        user_prefix: str = "user_"
    ):
        """
        Initialize prompt loader.

        Args:
            prompts_dir: Directory containing prompt markdown files
            system_prefix: Prefix for system prompts
            user_prefix: Prefix for user prompts
        """
        self.prompts_dir = Path(prompts_dir)
        self.system_prefix = system_prefix
        self.user_prefix = user_prefix

        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory does not exist: {prompts_dir}")
            self.prompts_dir.mkdir(parents=True, exist_ok=True)

    def load_prompt(self, filename: str) -> str:
        """
        Load a single prompt file.

        Args:
            filename: Name of the prompt file

        Returns:
            Prompt content as string
        """
        filepath = self.prompts_dir / filename

        if not filepath.exists():
            logger.warning(f"Prompt file not found: {filepath}")
            return ""

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        logger.debug(f"Loaded prompt: {filename}")
        return content

    def load_system_prompts(self) -> Dict[str, str]:
        """
        Load all system prompts.

        Returns:
            Dictionary of prompt name to content
        """
        prompts = {}

        for file in self.prompts_dir.glob(f"{self.system_prefix}*.md"):
            name = file.stem
            prompts[name] = self.load_prompt(file.name)

        logger.info(f"Loaded {len(prompts)} system prompts")
        return prompts

    def load_user_prompts(self) -> Dict[str, str]:
        """
        Load all user prompts.

        Returns:
            Dictionary of prompt name to content
        """
        prompts = {}

        for file in self.prompts_dir.glob(f"{self.user_prefix}*.md"):
            name = file.stem
            prompts[name] = self.load_prompt(file.name)

        logger.info(f"Loaded {len(prompts)} user prompts")
        return prompts

    def format_prompt(self, template: str, **kwargs) -> str:
        """
        Format a prompt template with variables.

        Args:
            template: Prompt template string
            **kwargs: Variables to substitute

        Returns:
            Formatted prompt
        """
        return template.format(**kwargs)


class AnswerGenerator:
    """
    Generates answers using LLM based on retrieved context.
    """

    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        Initialize answer generator.

        Args:
            provider: LLM provider (openai, anthropic, local)
            model: Model name
            api_key: API key (or None to use environment variable)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        self.provider = provider.lower()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize client based on provider
        if self.provider == "openai":
            self._init_openai(api_key)
        elif self.provider == "anthropic":
            self._init_anthropic(api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        logger.info(f"Initialized {provider} generator with model {model}")

    def _init_openai(self, api_key: Optional[str]):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI not installed. Install with: pip install openai")

        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not provided")

        self.client = OpenAI(api_key=api_key)

    def _init_anthropic(self, api_key: Optional[str]):
        """Initialize Anthropic client."""
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("Anthropic not installed. Install with: pip install anthropic")

        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key not provided")

        self.client = Anthropic(api_key=api_key)

    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Format retrieved results into context string.

        Args:
            results: List of search results

        Returns:
            Formatted context string
        """
        if not results:
            return "Nu au fost găsite date relevante."

        context_parts = []

        for i, result in enumerate(results, 1):
            metadata = result["metadata"]
            score = result.get("score", 0)

            parts = [f"\n### Document {i} (Relevanta: {score:.2f})"]

            if metadata.get("client_name"):
                parts.append(f"**Companie:** {metadata['client_name']}")

            if metadata.get("source_type"):
                parts.append(f"**Sursa energie:** {metadata['source_type']}")

            if metadata.get("power_installed"):
                parts.append(f"**Putere instalata:** {metadata['power_installed']} MW")

            if metadata.get("connection_point"):
                parts.append(f"**Loc racordare:** {metadata['connection_point']}")

            if metadata.get("address"):
                parts.append(f"**Adresa:** {metadata['address']}")

            if metadata.get("contact_person"):
                parts.append(f"**Contact:** {metadata['contact_person']}")

            if metadata.get("contact_phone"):
                parts.append(f"**Telefon:** {metadata['contact_phone']}")

            if metadata.get("contact_email"):
                parts.append(f"**Email:** {metadata['contact_email']}")

            # Source information
            source_info = []
            if metadata.get("source_file"):
                source_info.append(f"Fisier: {metadata['source_file']}")
            if metadata.get("source_sheet"):
                source_info.append(f"Sheet: {metadata['source_sheet']}")
            if metadata.get("row_number"):
                source_info.append(f"Rand: {metadata['row_number']}")

            if source_info:
                parts.append(f"*Sursa: {', '.join(source_info)}*")

            context_parts.append("\n".join(parts))

        return "\n".join(context_parts)

    def generate_answer(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None,
        user_prompt_template: Optional[str] = None
    ) -> str:
        """
        Generate answer using LLM.

        Args:
            query: User query
            context: Retrieved context
            system_prompt: System prompt
            user_prompt_template: User prompt template

        Returns:
            Generated answer
        """
        # Default system prompt
        if system_prompt is None:
            system_prompt = """Ești un expert în domeniul energiei electrice din România, specializat în
analiza furnizorilor și consumatorilor de energie. Răspunzi doar pe baza informațiilor furnizate în context.
Dacă informația nu există în context, spune-o clar."""

        # Default user prompt template
        if user_prompt_template is None:
            user_prompt_template = """Pe baza următoarelor date:

{context}

Răspunde la întrebarea: {question}

Furnizează:
1. Răspuns direct și concis
2. Date relevante (putere, locație, tip sursă)
3. Sursa informației
4. Observații suplimentare dacă sunt relevante"""

        # Format user prompt
        user_prompt = user_prompt_template.format(context=context, question=query)

        # Generate based on provider
        if self.provider == "openai":
            return self._generate_openai(system_prompt, user_prompt)
        elif self.provider == "anthropic":
            return self._generate_anthropic(system_prompt, user_prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _generate_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Generate answer using OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            answer = response.choices[0].message.content
            logger.debug(f"Generated answer with {response.usage.total_tokens} tokens")

            return answer

        except Exception as e:
            logger.error(f"Error generating answer with OpenAI: {e}")
            raise

    def _generate_anthropic(self, system_prompt: str, user_prompt: str) -> str:
        """Generate answer using Anthropic."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            answer = response.content[0].text
            logger.debug(f"Generated answer with Anthropic")

            return answer

        except Exception as e:
            logger.error(f"Error generating answer with Anthropic: {e}")
            raise

    def generate_with_prompts(
        self,
        query: str,
        results: List[Dict[str, Any]],
        system_prompt: str,
        user_prompt_template: str
    ) -> str:
        """
        Generate answer with custom prompts.

        Args:
            query: User query
            results: Search results
            system_prompt: System prompt
            user_prompt_template: User prompt template

        Returns:
            Generated answer
        """
        context = self.format_context(results)
        return self.generate_answer(query, context, system_prompt, user_prompt_template)


class ReportGenerator:
    """
    Generates structured reports from search results.
    """

    def __init__(self, answer_generator: Optional[AnswerGenerator] = None):
        """
        Initialize report generator.

        Args:
            answer_generator: Optional AnswerGenerator instance for LLM-enhanced reports
        """
        self.answer_generator = answer_generator

    def generate_markdown_report(
        self,
        query: str,
        results: List[Dict[str, Any]],
        statistics: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate markdown report.

        Args:
            query: Search query
            results: Search results
            statistics: Optional statistics

        Returns:
            Markdown formatted report
        """
        report_parts = [
            f"# Raport Analiza Energie",
            f"\n## Query: {query}",
            f"\n**Data:** {self._get_timestamp()}",
            f"\n**Numar rezultate:** {len(results)}",
        ]

        # Add statistics if available
        if statistics:
            report_parts.append("\n## Statistici")
            for key, value in statistics.items():
                report_parts.append(f"- **{key}:** {value}")

        # Add results
        report_parts.append("\n## Rezultate\n")

        for i, result in enumerate(results, 1):
            metadata = result["metadata"]
            score = result.get("score", 0)

            report_parts.append(f"### {i}. {metadata.get('client_name', 'N/A')} (Score: {score:.2f})")

            if metadata.get("source_type"):
                report_parts.append(f"- **Tip energie:** {metadata['source_type']}")

            if metadata.get("power_installed"):
                report_parts.append(f"- **Putere:** {metadata['power_installed']} MW")

            if metadata.get("address"):
                report_parts.append(f"- **Locație:** {metadata['address']}")

            if metadata.get("connection_point"):
                report_parts.append(f"- **Racordare:** {metadata['connection_point']}")

            # Contacts
            contacts = []
            if metadata.get("contact_person"):
                contacts.append(f"Persoană: {metadata['contact_person']}")
            if metadata.get("contact_phone"):
                contacts.append(f"Tel: {metadata['contact_phone']}")
            if metadata.get("contact_email"):
                contacts.append(f"Email: {metadata['contact_email']}")

            if contacts:
                report_parts.append(f"- **Contact:** {', '.join(contacts)}")

            report_parts.append("")

        return "\n".join(report_parts)

    def generate_summary(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> str:
        """
        Generate natural language summary using LLM.

        Args:
            query: Search query
            results: Search results

        Returns:
            Summary text
        """
        if not self.answer_generator:
            raise ValueError("AnswerGenerator required for summary generation")

        system_prompt = """Ești un analist în domeniul energiei electrice.
Creează un sumar concis și informativ al rezultatelor de căutare."""

        user_prompt = f"""Bazat pe următoarele rezultate pentru query-ul "{query}":

{{context}}

Creează un sumar executiv care include:
1. Numărul total de rezultate găsite
2. Principalele tipuri de surse de energie identificate
3. Puterea totală instalată
4. Regiunile geografice acoperite
5. Observații notabile"""

        context = self.answer_generator.format_context(results)
        user_prompt_formatted = user_prompt.format(context=context)

        return self.answer_generator.generate_answer(
            query,
            context,
            system_prompt,
            user_prompt_formatted
        )

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def save_report(self, report: str, output_path: str):
        """
        Save report to file.

        Args:
            report: Report content
            output_path: Output file path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        logger.info(f"Saved report to {output_path}")
