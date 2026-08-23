import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { AboutPage } from "./pages/AboutPage";
import { AdminAboutPage } from "./pages/AdminAboutPage";
import { AdminEditorPage } from "./pages/AdminEditorPage";
import { AdminLoginPage } from "./pages/AdminLoginPage";
import { AdminPostsPage } from "./pages/AdminPostsPage";
import { HomePage } from "./pages/HomePage";
import { PostPage } from "./pages/PostPage";
import { RequireAdmin } from "./pages/RequireAdmin";
import { SearchPage } from "./pages/SearchPage";
import { TagArticlesPage, TagsPage } from "./pages/TagsPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/posts/:slug" element={<PostPage />} />
          <Route path="/tags" element={<TagsPage />} />
          <Route path="/tags/:slug" element={<TagArticlesPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/admin/login" element={<AdminLoginPage />} />
        </Route>
        <Route element={<Layout admin />}>
          <Route element={<RequireAdmin />}>
            <Route path="/admin/posts" element={<AdminPostsPage />} />
            <Route path="/admin/posts/new" element={<AdminEditorPage />} />
            <Route path="/admin/posts/:id/edit" element={<AdminEditorPage />} />
            <Route path="/admin/about" element={<AdminAboutPage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
