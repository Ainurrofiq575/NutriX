/**
 * ImageUploadMenu Component
 * Provides a dropdown menu for image upload options (photo selection or camera capture)
 */
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { ImageIcon, Camera } from "lucide-react";

interface ImageUploadMenuProps {
  onPhotoSelect: () => void; // Handler for photo selection
  onCameraCapture: () => void; // Handler for camera capture
  disabled?: boolean; // Disables the menu when loading
}

export const ImageUploadMenu = ({
  onPhotoSelect,
  onCameraCapture,
  disabled,
}: ImageUploadMenuProps) => (
  <DropdownMenu>
    <DropdownMenuTrigger asChild>
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="h-8 w-8"
        disabled={disabled}
      >
        <ImageIcon className="h-4 w-4" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end" className="w-48">
      <DropdownMenuItem onClick={onPhotoSelect} className="gap-2">
        <ImageIcon className="h-4 w-4 hover:text-primary" />
        <span>Pilih Foto</span>
      </DropdownMenuItem>
      <DropdownMenuItem
        onClick={onCameraCapture}
        className="gap-2  md:hidden flex "
      >
        <Camera className="h-4 w-4 hover:text-primary" />
        <span>Ambil Foto</span>
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
);
