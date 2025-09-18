"use client";

import * as React from "react";
import { CalendarIcon } from "lucide-react";

import { cn } from "./utils";
import { Button } from "./button";
import { Calendar } from "./calendar";
import { Popover, PopoverContent, PopoverTrigger } from "./popover";

interface DateRange {
  from: Date | undefined;
  to?: Date | undefined;
}

interface DatePickerWithRangeProps extends React.HTMLAttributes<HTMLDivElement> {
  date: DateRange | undefined;
  setDate: (date: DateRange | undefined) => void;
}

const formatDate = (date: Date) => {
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    year: 'numeric' 
  });
};

export function DatePickerWithRange({
  className,
  date,
  setDate,
}: DatePickerWithRangeProps) {
  return (
    <div className={cn("grid gap-2", className)}>
      <Popover>
        <PopoverTrigger asChild>
          <Button
            id="date"
            variant={"outline"}
            className={cn(
              "w-[300px] justify-start text-left font-normal bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white hover:bg-[rgba(244,208,63,0.05)]",
              !date && "text-muted-foreground"
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {date?.from ? (
              date.to ? (
                <>
                  {formatDate(date.from)} - {formatDate(date.to)}
                </>
              ) : (
                formatDate(date.from)
              )
            ) : (
              <span>Pick a date range</span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent 
          className="w-auto p-0 bg-[#1A1D29] border-[rgba(244,208,63,0.2)]" 
          align="start"
        >
          <div className="p-4 text-white">
            <p className="text-sm text-[#B8BCC8] mb-2">Select date range</p>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-xs text-[#B8BCC8]">From</label>
                <input 
                  type="date" 
                  className="w-full mt-1 bg-[#0B0D14] border border-[rgba(244,208,63,0.2)] rounded px-2 py-1 text-white [color-scheme:dark]"
                  value={date?.from ? date.from.toISOString().split('T')[0] : ''}
                  onChange={(e) => {
                    const newDate = e.target.value ? new Date(e.target.value) : undefined;
                    setDate({ from: newDate, to: date?.to });
                  }}
                />
              </div>
              <div>
                <label className="text-xs text-[#B8BCC8]">To</label>
                <input 
                  type="date" 
                  className="w-full mt-1 bg-[#0B0D14] border border-[rgba(244,208,63,0.2)] rounded px-2 py-1 text-white [color-scheme:dark]"
                  value={date?.to ? date.to.toISOString().split('T')[0] : ''}
                  onChange={(e) => {
                    const newDate = e.target.value ? new Date(e.target.value) : undefined;
                    setDate({ from: date?.from, to: newDate });
                  }}
                />
              </div>
            </div>
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
}