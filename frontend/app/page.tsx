/**
 * Nutrix AI Web Application
 * ------------------------
 * Aplikasi web untuk analisis nutrisi makanan menggunakan AI.
 * Mendukung input teks dan gambar, dengan dua model AI:
 * - Gemini: Model AI dari Google untuk analisis umum
 * - Nutrix: Model khusus untuk analisis nutrisi dari database
 */

"use client";

import { useState, useRef } from "react";
import { Header } from "@/components/Header";
import { EmptyState } from "@/components/EmptyState";
import { MessageCard, type Message } from "@/components/MessageCard";
import { InputArea } from "@/components/InputArea";

export default function Home() {
  // State Management
  const [loading, setLoading] = useState(false); // Status loading saat request
  const [selectedImage, setSelectedImage] = useState<string | null>(null); // Preview gambar yang dipilih
  const [imageFile, setImageFile] = useState<File | null>(null); // File gambar untuk upload
  const [messages, setMessages] = useState<Message[]>([]); // Riwayat chat/pesan
  const [selectedModel, setSelectedModel] = useState<"gemini" | "nutrix">(
    "gemini"
  ); // Model AI yang dipilih
  const messagesEndRef = useRef<HTMLDivElement>(null); // Ref untuk auto-scroll

  /**
   * Menghapus pesan dari riwayat chat
   * @param id ID pesan yang akan dihapus
   */
  const handleDelete = (id: string) => {
    setMessages(messages.filter((message) => message.id !== id));
  };

  /**
   * Menambahkan pesan error ke riwayat chat
   * @param error Pesan error yang akan ditampilkan
   */
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

  /**
   * Fungsi utama untuk menganalisis makanan
   * Mengirim request ke API dan menangani respons
   *
   * @param type Tipe input ('text' atau 'image')
   * @param input Data input (string untuk teks, File untuk gambar)
   */
  const analyzeFood = async (type: "text" | "image", input: string | File) => {
    try {
      setLoading(true);
      if (!input) return;

      // Persiapkan data untuk dikirim ke API
      let payload: { text?: string; image?: File; model: "gemini" | "nutrix" } =
        {
          model: selectedModel,
        };

      // Set payload berdasarkan tipe input
      if (type === "image" && input instanceof File) {
        payload = { ...payload, image: input };
      } else if (type === "text" && typeof input === "string") {
        payload = { ...payload, text: input };
      } else {
        throw new Error("Invalid input type");
      }

      // Tambahkan pesan user ke riwayat
      const newMessage: Message = {
        id: Date.now().toString(),
        type,
        input: selectedImage || input.toString(),
        sender: "user",
      };
      setMessages((prev) => [...prev, newMessage]);

      // Reset input setelah submit
      setSelectedImage(null);
      setImageFile(null);

      // Kirim request ke API
      const formData = new FormData();
      if (payload.image) {
        formData.append("image", payload.image);
      } else if (payload.text) {
        formData.append("text", payload.text);
      }
      formData.append("model", payload.model);

      // Proses response dari API
      const response = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (data.success) {
        // Tambahkan respons AI ke riwayat
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

  /**
   * Handler untuk upload gambar via input file
   */
  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleImageFile(file);
  };

  /**
   * Handler untuk memproses file gambar
   * Mendukung upload, drag & drop, dan paste
   */
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

  /**
   * Handler untuk submit form
   * Menentukan tipe input dan memanggil analyzeFood
   */
  const handleSubmit = (text: string) => {
    if (imageFile) {
      analyzeFood("image", imageFile);
    } else if (text.trim()) {
      analyzeFood("text", text);
    }
  };

  return (
    <div className="flex flex-col min-h-[100dvh]">
      {/* Header dengan Model Selector */}
      <Header selectedModel={selectedModel} onModelChange={setSelectedModel} />

      {/* Area Chat/Pesan */}
      <main
        className="flex-1 overflow-y-auto overflow-x-hidden pb-[100px] md:pb-[120px]"
        ref={messagesEndRef}
      >
        <div className="max-w-3xl mx-auto p-4 space-y-4">
          {/* Tampilkan EmptyState jika belum ada pesan */}
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

          {/* Loading indicator */}
          {loading && (
            <div className="flex gap-2 items-center text-gray-500 animate-pulse">
              <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
              <div
                className="w-2 h-2 bg-primary rounded-full animate-bounce"
                style={{ animationDelay: "150ms" }}
              />
              <div
                className="w-2 h-2 bg-primary rounded-full animate-bounce"
                style={{ animationDelay: "300ms" }}
              />
            </div>
          )}
        </div>
      </main>

      {/* Area Input */}
      <div className="fixed bottom-0 left-0 right-0 pt-4">
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
