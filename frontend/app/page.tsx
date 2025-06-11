"use client";

import { useState, useRef } from "react";
import { Header } from "@/components/Header";
import { EmptyState } from "@/components/EmptyState";
import { MessageCard, type Message } from "@/components/MessageCard";
import { InputArea } from "@/components/InputArea";

export default function Home() {
  // State management
  const [loading, setLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Handler untuk menghapus pesan
  const handleDelete = (id: string) => {
    setMessages(messages.filter((message) => message.id !== id));
  };

  // Handler untuk menambahkan pesan error
  const addErrorMessage = (error: string) => {
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        type: "text",
        input: "",
        sender: "ai",
        error: true,
        result: {
          content: `⚠️ Error: ${error}\n\nSilakan coba lagi atau gunakan input yang berbeda.`,
        },
      },
    ]);
  };

  // Fungsi utama untuk analisis makanan
  const analyzeFood = async (type: "text" | "image", input: string | File) => {
    try {
      setLoading(true);
      if (!input) return;

      // Persiapkan payload
      let payload: { text?: string; image?: File } = {};
      if (type === "image" && input instanceof File) {
        payload = { image: input };
      } else if (type === "text" && typeof input === "string") {
        payload = { text: input };
      } else {
        throw new Error("Invalid input type");
      }

      // Tambahkan pesan user
      const newMessage: Message = {
        id: Date.now().toString(),
        type,
        input: selectedImage || input.toString(),
        sender: "user",
      };
      setMessages((prev) => [...prev, newMessage]);

      // Reset input
      setSelectedImage(null);
      setImageFile(null);

      // Kirim request ke API
      const formData = new FormData();
      if (payload.image) {
        formData.append("image", payload.image);
      } else if (payload.text) {
        formData.append("text", payload.text);
      }

      const response = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (data.success) {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now().toString(),
            type: "text",
            input: "",
            sender: "ai",
            result: data.data,
          },
        ]);
      } else {
        addErrorMessage(data.error);
      }
    } catch (error) {
      console.error("Error:", error);
      addErrorMessage("Terjadi kesalahan saat menganalisis makanan");
    } finally {
      setLoading(false);
    }
  };

  // Handlers untuk input gambar
  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleImageFile(file);
  };

  const handleImageFile = (file: File) => {
    if (file.type.startsWith("image/")) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setSelectedImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // Handler untuk form submission
  const handleSubmit = (text: string) => {
    if (imageFile) {
      analyzeFood("image", imageFile);
    } else if (text.trim()) {
      analyzeFood("text", text);
    }
  };

  return (
    <div className="flex flex-col min-h-[100dvh] ">
      <Header />

      {/* Area Pesan */}
      <main
        className="flex-1 overflow-y-auto overflow-x-hidden pb-[100px] md:pb-[120px]"
        ref={messagesEndRef}
      >
        <div className="max-w-3xl mx-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <EmptyState />
          ) : (
            messages.map((message) => (
              <MessageCard
                key={message.id}
                message={message}
                onDelete={handleDelete}
              />
            ))
          )}
          {loading && (
            <div className="flex gap-2 items-center text-gray-500 animate-pulse">
              <div className="w-2 h-2  bg-primary rounded-full animate-bounce" />
              <div
                className="w-2 h-2  bg-primary rounded-full animate-bounce"
                style={{ animationDelay: "150ms" }}
              />
              <div
                className="w-2 h-2  bg-primary rounded-full animate-bounce"
                style={{ animationDelay: "300ms" }}
              />
            </div>
          )}
        </div>
      </main>

      {/* Area Input */}
      <div className="fixed bottom-0 left-0 right-0  pt-4">
        <div className="max-w-3xl mx-auto px-4 bg-background">
          <InputArea
            selectedImage={selectedImage}
            setSelectedImage={setSelectedImage}
            loading={loading}
            onSubmit={handleSubmit}
            handleImageUpload={handleImageUpload}
            onDrop={handleImageFile}
            onPaste={handleImageFile}
          />
        </div>
      </div>
    </div>
  );
}
