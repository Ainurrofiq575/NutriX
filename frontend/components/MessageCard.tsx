import { Button } from "@/components/ui/button";
import { Trash2, Copy, RefreshCw, AlertCircle, Check } from "lucide-react";
import Image from "next/image";
import ReactMarkdown from "react-markdown";
import { useState } from "react";

// Interface untuk struktur pesan
export interface Message {
  id: string;
  type: "text" | "image"; // Tipe input pesan
  input: string; // Teks input atau URL gambar
  sender: "user" | "ai"; // Pengirim pesan
  result?: {
    content: string; // Hasil analisis AI
  };
  error?: boolean; // Status error
}

interface MessageCardProps {
  message: Message;
  onDelete: (id: string) => void;
}

// Komponen untuk menampilkan pesan dalam chat
export const MessageCard = ({ message, onDelete }: MessageCardProps) => {
  const [isCopied, setIsCopied] = useState(false);

  // Handler untuk menyalin teks ke clipboard
  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  // Render pesan dari user
  if (message.sender === "user") {
    return (
      <div className="flex justify-end mb-6">
        <div className="max-w-[85%] md:max-w-[75%] space-y-2">
          {message.type === "image" && message.input && (
            <div className="border rounded-lg overflow-hidden">
              <Image
                src={message.input}
                alt="Makanan"
                className="w-full object-contain max-h-[300px]"
                width={400}
                height={300}
              />
            </div>
          )}
          {message.type === "text" && (
            <div className="flex justify-end">
              <p className="bg-primary text-primary-foreground rounded-2xl rounded-tr-sm py-2 px-3 text-sm">
                {message.input}
              </p>
            </div>
          )}
          <div className="flex justify-end">
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={() => onDelete(message.id)}
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Render pesan dari AI
  return (
    <div className="flex gap-3 mb-6 animate-fade-in">
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
          message.error
            ? "bg-destructive text-destructive-foreground"
            : "bg-primary/10 text-primary"
        }`}
      >
        {message.error ? (
          <AlertCircle className="h-4 w-4" />
        ) : (
          <RefreshCw className="h-4 w-4" />
        )}
      </div>
      <div className="flex-1 space-y-2">
        <div className="prose prose-sm md:prose-base max-w-none dark:prose-invert">
          {message.result?.content ? (
            message.result.content.startsWith('Error:') ? (
              <p className="text-sm text-destructive">{message.result.content}</p>
            ) : (
              <div className="whitespace-pre-wrap text-sm md:text-base">
                {message.result.content.split('\n').map((line, index) => (
                  <p key={index} className="mb-1">
                    {line}
                  </p>
                ))}
              </div>
            )
          ) : (
            <p className="text-sm text-muted-foreground">
              {message.error ? "Error analyzing food" : "Analyzing food..."}
            </p>
          )}
        </div>
        <div className="flex gap-2">
          {!message.error && message.result?.content && !message.result.content.startsWith('Error:') && (
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={() => message.result?.content && copyToClipboard(message.result.content)}
            >
              {isCopied ? (
                <Check className="h-3 w-3" />
              ) : (
                <Copy className="h-3 w-3" />
              )}
            </Button>
          )}
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={() => onDelete(message.id)}
          >
            <Trash2 className="h-3 w-3" />
          </Button>
        </div>
      </div>
    </div>
  );
};
