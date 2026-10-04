import React, { useState, useEffect, useCallback } from "react";
import API from "../api";
import { categoryForSearch } from "../utils/translations";
import { useLanguage } from "../utils/LanguageContext";
import { useTranslatedValues } from "../utils/useTranslatedValues";

const ArtisanProductCard = ({ product, onDelete, getCategoryLabel }) => {
  const { t } = useLanguage();
  const { values, error, isTranslating } = useTranslatedValues([
    product.title || product.name || "",
    product.description || ""
  ]);

  return (
    <div
      style={{
        background: "#fafafa",
        border: "1px solid #ddd",
        borderRadius: "10px",
        padding: "15px",
        boxShadow: "0 2px 6px rgba(0,0,0,0.05)"
      }}
      aria-busy={isTranslating}
    >
      {product.image && (
        <img
          src={product.image?.startsWith("/uploads") ? `${API.defaults.baseURL}${product.image}` : product.image}
          alt={values[0] || (
            isTranslating ? t.translatingProduct : error ? t.productTranslationUnavailable : t.unnamedProduct
          )}
          style={{ width: "100%", borderRadius: "8px", marginBottom: "10px" }}
        />
      )}
      <h4>
        {values[0] || (
          isTranslating ? t.translatingProduct : error ? t.productTranslationUnavailable : t.unnamedProduct
        )}
      </h4>
      {error && <p role="status">{t.translationFailed}</p>}
      <p><strong>{t.price}:</strong> ₹{product.price}</p>
      <p><strong>{t.category}:</strong> {getCategoryLabel(product.category)}</p>
      <p><strong>{t.artisan}:</strong> {product.artisan_name} ({product.location})</p>
      <p>
        <strong>{t.description}:</strong>{" "}
        {values[1] || (
          isTranslating ? t.translatingProduct : error ? t.productTranslationUnavailable : t.noDescription
        )}
      </p>
      <button
        onClick={() => onDelete(product.id)}
        style={{
          background: "#DC143C",
          color: "#fff",
          borderRadius: "6px",
          padding: "5px 10px",
          marginTop: "10px"
        }}
      >
        🗑️ {t.delete}
      </button>
    </div>
  );
};

const ArtisanDashboard = ({ handleLogout }) => {
  const { t } = useLanguage();
  const [note, setNote] = useState("");
  const [status, setStatus] = useState(null);
  const [products, setProducts] = useState([]);
  const [isSavingProduct, setIsSavingProduct] = useState(false);
  const [productError, setProductError] = useState("");

  const getProductErrorMessage = useCallback((error, fallback) => {
    if (error.response?.status === 401) {
      return t.invalidArtisanSession;
    }
    if (error.response?.status === 403) {
      return t.artisanAccountRequired;
    }
    const detail = error.response?.data?.detail;
    if (Array.isArray(detail)) return detail.map((issue) => issue.msg).join(" ");
    return detail || fallback;
  }, [t]);
  const [productForm, setProductForm] = useState({
    name: "",
    price: "",
    category: "",
    description: "",
    artisan_name: "",
    location: "",
    image: null, // ✅ Added image field
  });

  const showStatus = useCallback((msg, type) => {
    setStatus({ msg, type });
    setTimeout(() => setStatus(null), 4000);
  }, []);

  // Load this artisan's saved data from the authenticated API.
  useEffect(() => {
    Promise.all([API.get("/artisan/notes"), API.get("/artisan/products")])
      .then(([notesResponse, productsResponse]) => {
        setNote(notesResponse.data.note || "");
        setProducts(productsResponse.data.products || []);
      })
      .catch((error) => {
        console.error(error);
        showStatus(getProductErrorMessage(error, t.loadingArtisanProducts), "error");
      });
  }, [getProductErrorMessage, showStatus, t]);

  const getCategoryLabel = (category) => {
    const categoryLabels = {
      home: t.homeDecorCategory,
      rukhwat: t.rukhwatArtCategory,
      pottery: t.potteryArtCategory,
      candle: t.candleResinCategory,
      jewellery: t.jewelleryArtCategory,
      spiritual: t.spiritualArtCategory
    };
    return categoryLabels[category] || category;
  };

  const saveNote = async () => {
    if (!note.trim()) {
      showStatus(`⚠️ ${t.noteRequired}`, "error");
      return;
    }
    try {
      await API.post("/artisan/notes", { note });
      showStatus(`✅ ${t.noteSaved}`, "success");
    } catch (error) {
      console.error(error);
      showStatus(t.noteSaveFailed, "error");
    }
  };

  const clearNote = async () => {
    if (window.confirm(t.confirmClear)) {
      try {
        await API.delete("/artisan/notes");
        setNote("");
        showStatus(`🗑️ ${t.noteCleared}`, "info");
      } catch (error) {
        console.error(error);
        showStatus(t.noteClearFailed, "error");
      }
    }
  };

  const [aiPrediction, setAiPrediction] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);

  // Trigger AI Categorization Engine on form change
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    const updated = { ...productForm, [name]: value };
    setProductForm(updated);

    if (name === "name" || name === "description") {
      if (updated.name.length > 2) {
        predictCategoryWithAI(updated.name, updated.description);
      }
    }
  };

  const predictCategoryWithAI = async (title, description) => {
    setAiLoading(true);
    try {
      const res = await fetch("http://localhost:8000/ml/categorize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: title,
          description: description || "",
          image_name: productForm.name
        })
      });
      if (res.ok) {
        const data = await res.json();
        setAiPrediction(data);
      }
    } catch (err) {
      console.warn("AI categorization notice:", err);
    } finally {
      setAiLoading(false);
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setProductForm((prev) => ({ ...prev, image: file }));
  };

  const applyAiCategory = () => {
    if (aiPrediction?.predictedCategory) {
      const category = categoryForSearch(aiPrediction.predictedCategory);
      if (!category) {
        showStatus(t.unavailableAiCategory, "error");
        return;
      }
      setProductForm((prev) => ({ ...prev, category }));
      showStatus(`${t.aiCategorySet} ${getCategoryLabel(category)}.`, "success");
    }
  };





  const addProduct = async (e) => {
    e.preventDefault();
    setIsSavingProduct(true);
    setProductError("");
    const formData = new FormData();
    formData.append("title", productForm.name.trim());
    formData.append("price", productForm.price);
    formData.append("category", productForm.category);
    formData.append("description", productForm.description);
    if (productForm.image) formData.append("image", productForm.image);

    try {
      const response = await API.post("/artisan/products", formData);
      setProducts((current) => [response.data.product, ...current]);
      setProductForm({
        name: "",
        price: "",
        category: "",
        description: "",
        artisan_name: "",
        location: "",
        image: null,
      });
      setProductError("");
      showStatus(`✅ ${t.productPublished}`, "success");
    } catch (error) {
      console.error(error);
      setProductError(getProductErrorMessage(error, t.productPublishFailed));
    } finally {
      setIsSavingProduct(false);
    }
  };

  const deleteProduct = async (id) => {
    if (!window.confirm(t.confirmDeleteProduct)) return;
    try {
      await API.delete(`/artisan/products/${id}`);
      setProducts((current) => current.filter((product) => product.id !== id));
      showStatus(`🗑️ ${t.productRemoved}`, "info");
    } catch (error) {
      console.error(error);
      showStatus(t.productDeleteFailed, "error");
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h1>🏺 Mittika</h1>
        <p>{t.artisanTagline}</p>
        <button
          onClick={handleLogout}
          style={{
            background: "#444",
            color: "#fff",
            padding: "8px 14px",
            borderRadius: "6px",
            marginTop: "10px",
            float: "right",
          }}
        >
          🚪 {t.navLogout}
        </button>
      </div>

      <div
        className="main-content"
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 2fr",
          gap: "20px",
          marginTop: "20px",
        }}
      >
        {/* Notepad Section */}
        <div
          className="notepad-section"
          style={{
            background: "#fff",
            padding: "20px",
            borderRadius: "12px",
            boxShadow: "0 4px 10px rgba(0,0,0,0.08)",
          }}
        >
          <h2>📝 {t.artisanNotepad}</h2>
          <textarea
            style={{
              width: "100%",
              height: "150px",
              borderRadius: "8px",
              border: "1px solid #ccc",
              padding: "10px",
              fontSize: "14px",
            }}
            placeholder={t.writeNotes}
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
          <div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
            <button
              style={{
                background: "#8B4513",
                color: "#fff",
                padding: "8px 14px",
                borderRadius: "6px",
              }}
              onClick={saveNote}
            >
              💾 {t.saveNote}
            </button>
            <button
              style={{
                background: "#2E8B57",
                color: "#fff",
                padding: "8px 14px",
                borderRadius: "6px",
              }}
              onClick={clearNote}
            >
              🗑️ {t.clear}
            </button>
          </div>
          {status && (
            <div
              style={{
                marginTop: "10px",
                padding: "10px",
                borderRadius: "6px",
                textAlign: "center",
                background:
                  status.type === "success"
                    ? "#e6ffed"
                    : status.type === "error"
                    ? "#ffe6e6"
                    : "#e6f7ff",
                color:
                  status.type === "success"
                    ? "#2E8B57"
                    : status.type === "error"
                    ? "#DC143C"
                    : "#005f99",
              }}
            >
              {status.msg}
            </div>
          )}
        </div>

        {/* Product Section */}
        <div
          className="products-section"
          style={{
            background: "#fff",
            padding: "20px",
            borderRadius: "12px",
            boxShadow: "0 4px 10px rgba(0,0,0,0.08)",
          }}
        >
          <h2>🛍️ {t.productManagement}</h2>
          {productError && <p role="alert" style={{ color: "#9B2C20", marginBottom: "12px" }}>{productError}</p>}
          <form onSubmit={addProduct}>
            <div style={{ marginBottom: "12px" }}>
              <label>{t.productName}:</label>
              <input
                type="text"
                name="name"
                value={productForm.name}
                onChange={handleFormChange}
                required
              />
            </div>
            <div style={{ marginBottom: "12px" }}>
              <label>{t.price} (₹):</label>
              <input
                type="number"
                min="0.01"
                step="0.01"
                name="price"
                value={productForm.price}
                onChange={handleFormChange}
                required
              />
            </div>
            {/* AI Product Categorization Engine Widget (CNN + NLP Hybrid) */}
            {aiPrediction && (
              <div style={{
                backgroundColor: "#FAF5EE",
                border: "1px solid #C85A32",
                borderRadius: "10px",
                padding: "12px",
                marginBottom: "14px",
                fontSize: "13px"
              }}>
                <div style={{ fontWeight: "bold", color: "#C85A32", marginBottom: "4px" }}>
                  🤖 {t.aiPredictedCategory}:
                </div>
                <div style={{ fontSize: "15px", fontWeight: "bold", color: "#362417" }}>
                  "{aiPrediction.predictedCategory}" ({(aiPrediction.confidence * 100).toFixed(1)}% {t.confidence})
                </div>
                <div style={{ height: "6px", backgroundColor: "#EFE5D8", borderRadius: "3px", margin: "6px 0", overflow: "hidden" }}>
                  <div style={{ height: "100%", width: `${aiPrediction.confidence * 100}%`, backgroundColor: "#C85A32" }}></div>
                </div>
                <button
                  type="button"
                  onClick={applyAiCategory}
                  style={{
                    backgroundColor: "#C85A32",
                    color: "#FFF",
                    border: "none",
                    padding: "4px 10px",
                    borderRadius: "6px",
                    fontSize: "12px",
                    cursor: "pointer",
                    fontWeight: "bold",
                    marginTop: "4px"
                  }}
                >
                  ✨ {t.applyPredictedCategory}
                </button>
              </div>
            )}

            <div style={{ marginBottom: "12px" }}>
              <label>{t.category}:</label>
              <select
                name="category"
                value={productForm.category}
                onChange={handleFormChange}
                required
              >

                <option value="">{t.selectCategory}</option>
                <option value="home">{t.homeStyling}</option>
                <option value="rukhwat">{t.navRukhwat}</option>
                <option value="pottery">{t.navPottery}</option>
                <option value="candle">{t.candleAndResin}</option>
                <option value="jewellery">{t.navJewellery}</option>
                <option value="spiritual">{t.spiritualArt}</option>
              </select>
            </div>
            <div style={{ marginBottom: "12px" }}>
              <label>{t.description}:</label>
              <textarea
                name="description"
                value={productForm.description}
                onChange={handleFormChange}
              />
            </div>
            <div style={{ marginBottom: "12px" }}>
              <label>{t.artisanName}:</label>
              <input
                type="text"
                name="artisan_name"
                value={productForm.artisan_name}
                onChange={handleFormChange}
              />
            </div>
            <div style={{ marginBottom: "12px" }}>
              <label>{t.location}:</label>
              <input
                type="text"
                name="location"
                value={productForm.location}
                onChange={handleFormChange}
              />
            </div>
            <div style={{ marginBottom: "12px" }}>
              <label>{t.productImage}:</label>
              <input type="file" accept="image/*" onChange={handleImageChange} />
            </div>
            <button
              type="submit"
              disabled={isSavingProduct}
              style={{
                background: "#8B4513",
                color: "#fff",
                padding: "8px 14px",
                borderRadius: "6px",
                marginTop: "10px",
              }}
            >
              {isSavingProduct ? t.publishing : `➕ ${t.addProduct}`}
            </button>
          </form>

          <h3 style={{ marginTop: "30px", color: "#8B4513" }}>
            📋 {t.yourProducts}
          </h3>
          {aiLoading && <p role="status">{t.aiCategorizerTitle}...</p>}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
              gap: "15px",
              marginTop: "10px",
            }}
          >
            {products.length === 0 ? (
              <p
                style={{
                  textAlign: "center",
                  color: "#666",
                  padding: "20px",
                }}
              >
                {t.noProducts}
              </p>
            ) : (
              products.map((product) => (
                <ArtisanProductCard
                  key={product.id}
                  product={product}
                  onDelete={deleteProduct}
                  getCategoryLabel={getCategoryLabel}
                />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArtisanDashboard;
