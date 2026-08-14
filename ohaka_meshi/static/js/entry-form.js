document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('entry-form');
  if (!form) return;

  setupTypeToggle();
  setupUrlAutoFetch();
  setupScreenshotPreview();
});

function setupTypeToggle() {
  const toggle = document.getElementById('type-toggle');
  const outFields = document.getElementById('out-fields');
  if (!toggle || !outFields) return;

  toggle.addEventListener('change', (event) => {
    if (event.target.name !== 'is_eating_out') return;
    outFields.hidden = event.target.value === '0';
  });
}

function setupUrlAutoFetch() {
  const urlInput = document.getElementById('reference_url');
  const dishInput = document.getElementById('dish_name');
  const restaurantInput = document.getElementById('restaurant_name');
  const locationInput = document.getElementById('location');
  const hiddenImage = document.getElementById('ogp_image_url');
  const preview = document.getElementById('url-preview');
  const previewImg = document.getElementById('url-preview-img');
  const previewText = document.getElementById('url-preview-text');
  if (!urlInput) return;

  const isEatingOut = () => {
    const checked = document.querySelector('input[name="is_eating_out"]:checked');
    return checked ? checked.value === '1' : true;
  };

  let lastFetchedUrl = '';

  const fetchMetadata = async () => {
    const url = urlInput.value.trim();
    if (!url || !/^https?:\/\//i.test(url) || url === lastFetchedUrl) return;
    lastFetchedUrl = url;

    previewText.textContent = '情報を取得中...';
    previewImg.hidden = true;
    preview.classList.add('visible');

    try {
      const res = await fetch('/api/fetch-url-metadata', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      const data = await res.json();

      if (!data.ok) {
        previewText.textContent = '自動取得できませんでした。手動で入力してください。';
        return;
      }

      if (data.title) {
        // 外食のURLはページ全体がお店の情報であることが多いため、
        // 取得したタイトルはレストラン名に、料理名は手動入力のままにする。
        // 内食（レシピサイト等）はタイトル=料理名であることが多いのでそちらへ。
        if (isEatingOut()) {
          if (restaurantInput && !restaurantInput.value.trim()) {
            restaurantInput.value = data.title;
          }
        } else if (!dishInput.value.trim()) {
          dishInput.value = data.title;
        }
      }
      if (data.location && locationInput && !locationInput.value.trim()) {
        locationInput.value = data.location;
      }
      if (data.image) {
        previewImg.src = data.image;
        previewImg.hidden = false;
        hiddenImage.value = data.image;
      }
      previewText.textContent = data.title || 'ページ情報を取得しました';
    } catch (err) {
      previewText.textContent = '自動取得できませんでした。手動で入力してください。';
    }
  };

  urlInput.addEventListener('blur', fetchMetadata);
  urlInput.addEventListener('paste', () => setTimeout(fetchMetadata, 50));
}

function setupScreenshotPreview() {
  const fileInput = document.getElementById('screenshot');
  const preview = document.getElementById('screenshot-preview');
  const previewImg = document.getElementById('screenshot-preview-img');
  const form = document.getElementById('entry-form');
  if (!fileInput || !form) return;

  const showPreview = (file) => {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      preview.classList.add('visible');
    };
    reader.readAsDataURL(file);
  };

  fileInput.addEventListener('change', () => {
    if (fileInput.files && fileInput.files[0]) {
      showPreview(fileInput.files[0]);
    }
  });

  form.addEventListener('paste', (event) => {
    const items = event.clipboardData && event.clipboardData.items;
    if (!items) return;
    for (const item of items) {
      if (item.type && item.type.startsWith('image/')) {
        const file = item.getAsFile();
        if (!file) continue;
        const dt = new DataTransfer();
        dt.items.add(file);
        fileInput.files = dt.files;
        showPreview(file);
        event.preventDefault();
        break;
      }
    }
  });
}
