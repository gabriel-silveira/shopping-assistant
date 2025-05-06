import Image from 'next/image';

const Header = () => {
  return (
    <header className="fixed top-0 left-0 right-0 w-full h-[100px] bg-cover bg-center z-50" style={{
      backgroundImage: 'url(/bg_header-interna.jpg)'
    }}>
      <div className="container mx-auto h-full flex items-center">
        <Image
          src="/logo.png"
          alt="CSN Logo"
          width={150}
          height={50}
          className="relative z-10"
        />
      </div>
      {/* Overlay escuro para melhorar contraste */}
      <div className="absolute inset-0 bg-black opacity-30"></div>
    </header>
  );
};

export default Header;
