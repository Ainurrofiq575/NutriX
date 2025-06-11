export const EmptyState = () => (
  <div className="h-[calc(100vh-180px)] flex flex-col items-center justify-center px-4">
    <div className="flex flex-col items-center gap-2 max-w-[600px] text-center">
      <h2 className="text-4xl font-semibold bg-gradient-to-r from-primary to-primary/80 text-transparent bg-clip-text">
        Selamat datang di Nutrix AI
      </h2>
      <p className="text-gray-500 text-sm font-medium">
        Ketik nama makanan atau upload foto untuk mengetahui kandungan nutrisi
        dan manfaatnya
      </p>
    </div>
  </div>
);
