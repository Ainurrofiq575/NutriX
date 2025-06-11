import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send, Trash2 } from "lucide-react";
import { useRef } from "react";
import { ImageUploadMenu } from "@/components/ImageUploadMenu";
import Image from "next/image";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";

// Schema validasi form
const formSchema = z.object({
  message: z.string().optional(),
});

type FormData = z.infer<typeof formSchema>;

// Props untuk komponen input
interface InputAreaProps {
  selectedImage: string | null; // URL preview gambar
  setSelectedImage: (image: string | null) => void;
  loading: boolean; // Status loading
  onSubmit: (text: string) => void;
  handleImageUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onDrop: (file: File) => void; // Handler drag & drop
  onPaste: (file: File) => void; // Handler paste gambar
}

// Komponen area input pesan dan upload gambar
export const InputArea = ({
  selectedImage,
  setSelectedImage,
  loading,
  onSubmit,
  handleImageUpload,
  onDrop,
  onPaste,
}: InputAreaProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  // Setup React Hook Form
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      message: "",
    },
  });

  // Handler untuk submit form
  const handleFormSubmit = (data: FormData) => {
    if (data.message?.trim() || selectedImage) {
      onSubmit(data.message || "");
      form.reset();
    }
  };

  // Handler untuk keyboard events
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey && !selectedImage) {
      e.preventDefault();
      form.handleSubmit(handleFormSubmit)();
    }
  };

  // Handlers untuk drag & drop
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) {
      onDrop(file);
    }
  };

  // Handler untuk paste gambar
  const handlePaste = (e: React.ClipboardEvent) => {
    const items = e.clipboardData.items;
    for (const item of items) {
      if (item.type.startsWith("image/")) {
        const file = item.getAsFile();
        if (file) {
          onPaste(file);
          break;
        }
      }
    }
  };

  // Handlers untuk menu upload
  const handlePhotoSelect = () => fileInputRef.current?.click();
  const handleCameraCapture = () => cameraInputRef.current?.click();

  return (
    <div className="bottom-0 left-0 right-0 p-4">
      <form
        onSubmit={form.handleSubmit(handleFormSubmit)}
        className="max-w-3xl mx-auto"
      >
        {selectedImage && (
          <div className="mb-4 relative">
            <Image
              src={selectedImage}
              alt="Preview"
              className="w-full max-h-[200px] object-contain rounded-lg"
              width={400}
              height={200}
            />
            <Button
              type="button"
              variant="destructive"
              size="icon"
              className="absolute top-2 right-2"
              onClick={() => setSelectedImage(null)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        )}
        <div
          className="relative flex items-center gap-2"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <Textarea
            {...form.register("message")}
            onKeyDown={handleKeyDown}
            onPaste={handlePaste}
            placeholder="Ketik nama makanan atau upload foto..."
            className="pr-24 min-h-0 py-5 resize-none text-xs md:text-sm bg-background"
            rows={1}
            disabled={!!selectedImage || loading}
          />
          <div className="absolute right-2 flex gap-2">
            <ImageUploadMenu
              onPhotoSelect={handlePhotoSelect}
              onCameraCapture={handleCameraCapture}
              disabled={loading}
            />
            <Button
              type="submit"
              size="icon"
              disabled={
                (!form.watch("message")?.trim() && !selectedImage) || loading
              }
              className="h-8 w-8"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            className="hidden"
          />
          <input
            ref={cameraInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handleImageUpload}
            className="hidden"
          />
        </div>
      </form>
    </div>
  );
};
