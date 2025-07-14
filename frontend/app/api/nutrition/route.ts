import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:5000";

// frontend/app/api/nutrition/route.ts (route untuk backend)
export async function POST(req: NextRequest) {
  try {
    const data = await req.json();                       // Ambil data dari user
    const { food_name, image_data, model } = data;

    // Validate backend connection first
    try {
      // Create FormData for the request(membuat formdata yang akan dikirim ke backend)
      const formData = new FormData();
      formData.append('model', model || 'nutrix');
      
      if (image_data) {
        // Convert base64 to blob
        const base64Response = await fetch(image_data);
        const blob = await base64Response.blob();
        formData.append('image', blob);
      } else if (food_name) {
        formData.append('text', food_name);
      }

      // konfigurasi request ke backend dengan api/analyze (Kirim ke backend)
      const response = await fetch(`${BACKEND_URL}/api/analyze`, {
        method: "POST",
        body: formData,
      });

      // Check if response is JSON
      const contentType = response.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        console.error("Backend error: Not JSON response", await response.text());
        return NextResponse.json(
          { 
            success: false, 
            error: "Backend server error. Please make sure the backend server is running on port 5000." 
          },
          { status: 502 }
        );
      }

      const result = await response.json();
      console.log('Backend response:', result); // Debug log

      if (!result.success) {
        return NextResponse.json(
          { success: false, error: result.error },
          { status: 400 }
        );
      }

      // Memformat data response untuk frontend
      let content = '';
      if (typeof result.data === 'string') {
        content = result.data;
      } else if (result.data.content) {
        content = result.data.content;
      } else if (typeof result.data === 'object') {
        content = JSON.stringify(result.data, null, 2);
      }

      return NextResponse.json({ 
        success: true, 
        data: content
      });
    } catch (error) {
      console.error("Backend connection error:", error);
      return NextResponse.json(
        { 
          success: false, 
          error: "Could not connect to backend server. Please make sure it's running on port 5000." 
        },
        { status: 502 }
      );
    }
  } catch (error) {
    console.error("Request parsing error:", error);
    return NextResponse.json(
      { success: false, error: "Invalid request format" },
      { status: 400 }
    );
  }
} 