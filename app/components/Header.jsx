export function Header() {
  return (
    <header className = "h-16 flex shadow-md bg-white p-4">
      <h1 className = "text-2xl font-bold">感情認識アプリ</h1>
      <nav className = "fixed right-0">
        <ul className = "flex space-x-8 mr-8 text-xl">
          <li><a href="/">ホーム</a></li>
          <li><a href="/detection">分析</a></li>
        </ul>
      </nav>
    </header>
  );
}