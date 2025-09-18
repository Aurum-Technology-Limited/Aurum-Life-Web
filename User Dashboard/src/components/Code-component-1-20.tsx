import React from 'react';
import { Search, Plus, Bell, MoonStar } from 'lucide-react';

export function Header() {
  return (
    <header className="sticky top-0 z-40 px-4 lg:px-6 py-4 border-b" style={{background: 'rgba(11,13,20,0.8)', backdropFilter: 'blur(16px)', borderColor: 'rgba(244,208,63,0.12)'}}>
      <div className="flex items-center justify-between gap-3">
        {/* Mobile Brand */}
        <div className="flex items-center gap-3 lg:hidden">
          <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{background: 'linear-gradient(135deg,#F4D03F,#F7DC6F)', color: '#0B0D14', fontWeight: '700'}}>
            AL
          </div>
          <span className="font-semibold tracking-tight">Aurum Life</span>
        </div>

        {/* Search */}
        <div className="hidden md:flex items-center flex-1 max-w-xl">
          <div className="w-full flex items-center gap-2 px-3 py-2 rounded-xl border" style={{background: 'rgba(26,29,41,0.6)', borderColor: 'rgba(244,208,63,0.15)'}}>
            <Search className="w-4 h-4" style={{color: '#B8BCC8'}} />
            <input 
              type="text" 
              placeholder="Search tasks, projects, pillars..." 
              className="w-full bg-transparent text-sm focus:outline-none placeholder:text-[#6B7280]"
            />
            <div className="text-[10px] px-2 py-1 rounded-md border" style={{borderColor: 'rgba(244,208,63,0.15)', color: '#B8BCC8'}}>
              /
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button className="hidden md:inline-flex items-center gap-2 text-xs font-medium px-3 py-2 rounded-lg border transition hover:opacity-90" style={{borderColor: 'rgba(244,208,63,0.25)', color: '#F4D03F'}}>
            <Plus className="w-4 h-4" />
            Quick Add
          </button>
          <button className="p-2 rounded-lg border hover:opacity-90" style={{borderColor: 'rgba(244,208,63,0.2)'}}>
            <Bell className="w-4 h-4" style={{color: '#B8BCC8'}} />
          </button>
          <button className="p-2 rounded-lg border hover:opacity-90" style={{borderColor: 'rgba(244,208,63,0.2)'}}>
            <MoonStar className="w-4 h-4" style={{color: '#B8BCC8'}} />
          </button>
          <img 
            src="https://images.unsplash.com/photo-1581065178026-390bc4e78dad?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwcm9mZXNzaW9uYWwlMjB3b21hbiUyMHBvcnRyYWl0fGVufDF8fHx8MTc1NzIwMTY3Nnww&ixlib=rb-4.1.0&q=80&w=64" 
            alt="Avatar" 
            className="w-8 h-8 rounded-full ring-1" 
            style={{ringColor: 'rgba(244,208,63,0.25)'}}
          />
        </div>
      </div>
    </header>
  );
}