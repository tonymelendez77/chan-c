import Link from "next/link";

export default function Footer() {
  return (
    <footer className="bg-[#1C2B3A] text-slate-400 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <p className="text-lg font-bold text-white mb-2">
              CHAN<span className="text-amber-400">-C</span>
            </p>
            <p className="text-sm">
              Marketplace de construcción para Guatemala. Conectamos empresas con trabajadores
              verificados.
            </p>
          </div>
          <div>
            <p className="text-sm font-semibold text-white mb-3">Plataforma</p>
            <div className="space-y-2 text-sm">
              <Link href="/register" className="block hover:text-white transition-colors">
                Registrar empresa
              </Link>
              <Link href="/login" className="block hover:text-white transition-colors">
                Iniciar sesión
              </Link>
            </div>
          </div>
          <div>
            <p className="text-sm font-semibold text-white mb-3">Contacto</p>
            <div className="space-y-2 text-sm">
              <p>info@chanc.gt</p>
              <p>Ciudad de Guatemala</p>
            </div>
          </div>
        </div>
        <div className="border-t border-slate-700 mt-8 pt-6 text-sm text-center">
          © {new Date().getFullYear()} CHAN-C. Todos los derechos reservados.
        </div>
      </div>
    </footer>
  );
}
