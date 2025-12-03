import React from "react";

export function parseMarkdown(text: string): React.ReactNode[] {
  if (!text) return [];

  const lines = text.split("\n");
  const elements: React.ReactNode[] = [];
  let currentParagraph: string[] = [];
  let currentListItems: React.ReactNode[] = [];
  let currentOrderedItems: React.ReactNode[] = [];
  let keyCounter = 0;

  const processParagraph = (para: string[]) => {
    if (para.length === 0) return;

    const paraText = para.join(" ");
    const processed = processInlineMarkdown(paraText, keyCounter);
    keyCounter += processed.length;
    
    if (processed.length > 0) {
      elements.push(
        <p key={keyCounter++} className="mb-2">
          {processed}
        </p>
      );
    }
  };

  const processInlineMarkdown = (text: string, startKey: number = 0): React.ReactNode[] => {
    const parts: React.ReactNode[] = [];
    let currentIndex = 0;
    let key = startKey;

    const boldRegex = /\*\*([^*]+)\*\*/g;
    let match;
    const boldMatches: Array<{ start: number; end: number; text: string }> = [];
    
    while ((match = boldRegex.exec(text)) !== null) {
      boldMatches.push({
        start: match.index,
        end: match.index + match[0].length,
        text: match[1],
      });
    }

    const italicRegex = /(?<!\*)\*([^*]+)\*(?!\*)|(?<!_)_([^_]+)_(?!_)/g;
    const italicMatches: Array<{ start: number; end: number; text: string }> = [];
    
    while ((match = italicRegex.exec(text)) !== null) {
      const isInsideBold = boldMatches.some(
        (b) => match!.index >= b.start && match!.index < b.end
      );
      if (!isInsideBold) {
        italicMatches.push({
          start: match.index,
          end: match.index + match[0].length,
          text: match[1] || match[2],
        });
      }
    }

    const allMatches = [
      ...boldMatches.map((m) => ({ ...m, type: "bold" as const })),
      ...italicMatches.map((m) => ({ ...m, type: "italic" as const })),
    ].sort((a, b) => a.start - b.start);

    for (const match of allMatches) {
      if (match.start > currentIndex) {
        const beforeText = text.substring(currentIndex, match.start);
        if (beforeText) {
          parts.push(beforeText);
        }
      }

      if (match.type === "bold") {
        parts.push(
          <strong key={key++} className="font-bold">
            {match.text}
          </strong>
        );
      } else {
        parts.push(
          <em key={key++} className="italic">
            {match.text}
          </em>
        );
      }

      currentIndex = match.end;
    }

    if (currentIndex < text.length) {
      parts.push(text.substring(currentIndex));
    }

    return parts.length > 0 ? parts : [text];
  };

  const flushList = () => {
    if (currentListItems.length > 0) {
      elements.push(
        <ul key={keyCounter++} className="list-disc mb-2 space-y-1 ml-4">
          {currentListItems}
        </ul>
      );
      currentListItems = [];
    }
    if (currentOrderedItems.length > 0) {
      elements.push(
        <ol key={keyCounter++} className="list-decimal mb-2 space-y-1 ml-4">
          {currentOrderedItems}
        </ol>
      );
      currentOrderedItems = [];
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    if (line.match(/^[-*]\s+/)) {
      if (currentParagraph.length > 0) {
        processParagraph(currentParagraph);
        currentParagraph = [];
      }
      flushList();

      const listItemText = line.replace(/^[-*]\s+/, "");
      const processed = processInlineMarkdown(listItemText, keyCounter);
      keyCounter += processed.length;
      
      currentListItems.push(
        <li key={keyCounter++} className="ml-4">{processed}</li>
      );
    } else if (line.match(/^\d+\.\s+/)) {
      if (currentParagraph.length > 0) {
        processParagraph(currentParagraph);
        currentParagraph = [];
      }
      if (currentListItems.length > 0) {
        elements.push(
          <ul key={keyCounter++} className="list-disc mb-2 space-y-1 ml-4">
            {currentListItems}
          </ul>
        );
        currentListItems = [];
      }

      const listItemText = line.replace(/^\d+\.\s+/, "");
      const processed = processInlineMarkdown(listItemText, keyCounter);
      keyCounter += processed.length;
      
      currentOrderedItems.push(
        <li key={keyCounter++} className="ml-4">{processed}</li>
      );
    } else if (line === "") {
      if (currentParagraph.length > 0) {
        processParagraph(currentParagraph);
        currentParagraph = [];
      }
      flushList();
    } else {
      flushList();
      currentParagraph.push(line);
    }
  }

  if (currentParagraph.length > 0) {
    processParagraph(currentParagraph);
  }
  flushList();

  return elements.length > 0 ? elements : [<p key="default">{text}</p>];
}
