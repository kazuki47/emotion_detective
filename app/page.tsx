'use client';
import Link from 'next/link';
import { Header } from './components/Header';
import Button from '@mui/material/Button';

export default function Home() {
  return (
    <div>
      <Header />
      <main className="flex flex-col items-center justify-between p-24">
        <h1 className="text-4xl font-bold">感情分析アプリ</h1>
        <Button component={Link} href="/detection" variant="contained" color="primary" sx={{mt:8}}>
          Start
        </Button>
      </main>
    </div>
  );
}
