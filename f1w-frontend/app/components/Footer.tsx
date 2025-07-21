export default function Footer() {
  return (
    <footer className="bg-[#15151e] text-white py-6 mt-12">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p className="text-sm">&copy; {new Date().getFullYear()} F1 Data Visualization</p>
          </div>
          <div className="flex space-x-4">
            <a href="https://github.com" className="text-gray-300 hover:text-white text-sm">
              GitHub
            </a>
            <a href="https://formula1.com" className="text-gray-300 hover:text-white text-sm">
              Formula 1
            </a>
            <a href="https://fastf1.readthedocs.io" className="text-gray-300 hover:text-white text-sm">
              FastF1
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
