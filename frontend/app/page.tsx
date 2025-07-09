/**
 * Nutrix AI Web Application
 * ------------------------
 * Aplikasi web untuk analisis nutrisi makanan menggunakan AI.
 * Mendukung input teks dan gambar, dengan dua model AI:
 * - Gemini: Model AI dari Google untuk analisis umum
 * - Nutrix: Model khusus untuk analisis nutrisi dari database
 */

"use client";

import { useState } from "react";
import { Header } from "@/components/Header";
import { EmptyState } from "@/components/EmptyState";
import { MessageCard, type Message } from "@/components/MessageCard";
import { InputArea } from "@/components/InputArea";
import { ModelSelect } from "@/components/model-select";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<"gemini" | "nutrix">("nutrix");

  // Handler untuk submit pesan
  const handleSubmit = async (text: string) => {
    if (loading) return;

    try {
      setLoading(true);

      // Buat ID unik untuk pesan
      const messageId = Date.now().toString();

      // Tambahkan pesan user ke state
      const userMessage: Message = {
        id: messageId,
        type: selectedImage ? "image" : "text",
        input: selectedImage || text,
        sender: "user",
      };

      setMessages((prev) => [...prev, userMessage]);

      let response;
      const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:5000";

      // Jika model Gemini dan ada gambar, kirim langsung ke backend
      if (selectedModel === "gemini" && selectedImage) {
        // Convert base64 to blob
        const base64Response = await fetch(selectedImage);
        const blob = await base64Response.blob();

        // Create FormData
        const formData = new FormData();
        formData.append('model', 'gemini');
        formData.append('image', blob, 'image.jpg'); // Add filename to help with mime type detection

        // Kirim langsung ke backend
        response = await fetch(`${BACKEND_URL}/api/analyze`, {
          method: "POST",
          body: formData,
        });
      } else {
        // Untuk kasus lain, gunakan API route Next.js
        response = await fetch("/api/nutrition", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            food_name: text,
            image_data: selectedImage,
            model: selectedModel,
          }),
        });
      }

      const data = await response.json();
      console.log('API Response:', data); // Debug log

      // Tambahkan pesan AI ke state
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          type: "text",
          input: "",
          sender: "ai",
          result: {
            content: data.success ? (data.data.content || data.data) : `Error: ${data.error}`,
          },
          error: !data.success,
        },
      ]);

      // Reset state
      setSelectedImage(null);
    } catch (error) {
      console.error("Error:", error);
      // Add error message
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          type: "text",
          input: "",
          sender: "ai",
          result: {
            content: "Terjadi kesalahan saat menganalisis makanan. Mohon coba lagi.",
          },
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Handler untuk upload gambar
  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setSelectedImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // Handler untuk drag & drop
  const handleDrop = (file: File) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      setSelectedImage(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  // Handler untuk paste gambar
  const handlePaste = (file: File) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      setSelectedImage(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  // Handler untuk hapus pesan
  const handleDeleteMessage = (id: string) => {
    setMessages((prev) => prev.filter((msg) => msg.id !== id));
  };

  return (
    <main className="flex min-h-screen flex-col">
      <Header>
        <ModelSelect
          selectedModel={selectedModel}
          onModelChange={setSelectedModel}
        />
      </Header>

      <div className="flex-1 pb-32">
        <div className="max-w-3xl mx-auto pt-8 px-4">
          {messages.length === 0 ? (
            <EmptyState />
          ) : (
            messages.map((message) => (
              <MessageCard
                key={message.id}
                message={message}
                onDelete={handleDeleteMessage}
              />
            ))
          )}
        </div>
      </div>

      <InputArea
        selectedImage={selectedImage}
        setSelectedImage={setSelectedImage}
        loading={loading}
        onSubmit={handleSubmit}
        handleImageUpload={handleImageUpload}
        onDrop={handleDrop}
        onPaste={handlePaste}
      />
    </main>
  );
}
