import React from 'react';

interface SearchProps {
  query: string;
  setQuery: React.Dispatch<React.SetStateAction<string>>;
}



const SearchBar= ({ query, setQuery }: SearchProps) => {
  return (
    <div className="relative mb-4">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search for students..."
        className="w-full px-4 py-2 bg-white border border-[#2596be] rounded-lg text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#2596be] transition"
      />

    </div>
  );
};

export default SearchBar;
