export async function extractTextFromFile(file: File): Promise<string> {
  const name = file.name.toLowerCase();

  if (name.endsWith(".txt") || name.endsWith(".md")) {
    return file.text();
  }

  if (name.endsWith(".pdf")) {
    return extractPdfText(file);
  }

  if (name.endsWith(".docx")) {
    return extractDocxText(file);
  }

  throw new Error("Formato nao suportado. Usa PDF, DOCX, TXT ou MD.");
}

async function extractPdfText(file: File): Promise<string> {
  const pdfjs = await import("pdfjs-dist");
  pdfjs.GlobalWorkerOptions.workerSrc = new URL(
    "pdfjs-dist/build/pdf.worker.mjs",
    import.meta.url,
  ).toString();

  const buffer = await file.arrayBuffer();
  const pdf = await pdfjs.getDocument({ data: buffer }).promise;
  const pages: string[] = [];

  for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber += 1) {
    const page = await pdf.getPage(pageNumber);
    const content = await page.getTextContent();
    pages.push(
      content.items
        .map((item) => ("str" in item ? item.str : ""))
        .join(" ")
        .trim(),
    );
  }

  const text = pages.filter(Boolean).join("\n\n").trim();
  if (!text) {
    throw new Error("Nao consegui extrair texto deste PDF.");
  }
  return text;
}

async function extractDocxText(file: File): Promise<string> {
  const mammoth = await import("mammoth/mammoth.browser");
  const buffer = await file.arrayBuffer();
  const result = await mammoth.extractRawText({ arrayBuffer: buffer });
  const text = result.value.trim();

  if (!text) {
    throw new Error("Nao consegui extrair texto deste DOCX.");
  }
  return text;
}
