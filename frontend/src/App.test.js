import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import VoiceSearchModal from './components/VoiceSearchModal';
import DummyPayment from './components/DummyPayment';
import ProductCard from './components/ProductCard';
import Signup from './components/Signup';
import Dashboard from './components/Dashboard';
import { LanguageContext } from './utils/LanguageContext';
import API from './api';

beforeEach(() => {
  localStorage.clear();
  API.get.mockReset();
  API.post.mockReset();
  API.get.mockResolvedValue({ data: { artisans: [] } });
  API.post.mockResolvedValue({ data: {} });
});

jest.mock('./api', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
    post: jest.fn(),
    create: jest.fn(() => ({ get: jest.fn(), post: jest.fn() }))
  }
}));

import App from './App';
import { categoryForSearch } from './utils/translations';

test('artisan signup collects artisan profile details and uploads a photo', async () => {
  const alert = jest.spyOn(window, 'alert').mockImplementation(() => {});
  render(
    <MemoryRouter>
      <LanguageContext.Provider value="en">
        <Signup />
      </LanguageContext.Provider>
    </MemoryRouter>
  );

  fireEvent.change(screen.getByLabelText('Full Name'), { target: { value: 'Asha Maker' } });
  fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'asha@example.com' } });
  fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'artisan-pass' } });
  fireEvent.change(screen.getByLabelText('Account Type'), { target: { value: 'artisan' } });
  fireEvent.change(screen.getByLabelText('City, state, or region'), { target: { value: 'Pune, Maharashtra' } });
  fireEvent.change(screen.getByLabelText('Years of experience'), { target: { value: '8' } });
  fireEvent.change(screen.getByLabelText('Craft or specialty'), { target: { value: 'Handmade jewellery' } });
  const photo = new File(['artisan-photo'], 'asha.png', { type: 'image/png' });
  fireEvent.change(screen.getByLabelText('Profile photo'), { target: { files: [photo] } });
  fireEvent.click(screen.getByRole('button', { name: 'Create Account' }));

  await waitFor(() => expect(alert).toHaveBeenCalledWith('Account created successfully!'));
  alert.mockRestore();
  const [path, formData] = API.post.mock.calls[0];
  expect(path).toBe('/auth/artisan-signup');
  expect(formData.get('name')).toBe('Asha Maker');
  expect(formData.get('location')).toBe('Pune, Maharashtra');
  expect(formData.get('experience')).toBe('8');
  expect(formData.get('craft')).toBe('Handmade jewellery');
  expect(formData.get('profile_photo')).toBe(photo);
});

test('homepage shows artisan cards with their profile photo and details', async () => {
  API.get.mockResolvedValue({
    data: {
      artisans: [{
        id: 'artisan-1',
        name: 'Asha Maker',
        location: 'Pune, Maharashtra',
        experience: 8,
        craft: 'Handmade jewellery',
        profilePhoto: '/uploads/artisans/asha.png'
      }]
    }
  });
  render(
    <MemoryRouter>
      <LanguageContext.Provider value="en">
        <Dashboard />
      </LanguageContext.Provider>
    </MemoryRouter>
  );

  expect(await screen.findByRole('heading', { name: 'Meet Our Artisans' })).toBeInTheDocument();
  expect(screen.getByRole('img', { name: 'Asha Maker' })).toHaveAttribute(
    'src',
    'http://127.0.0.1:8000/uploads/artisans/asha.png'
  );
  expect(screen.getByText('Pune, Maharashtra')).toBeInTheDocument();
  expect(screen.getByText('Handmade jewellery')).toBeInTheDocument();
});

test('renders the storefront hero heading', () => {
  render(<App />);
  expect(screen.getByText(/Crafted by Earth, Shaped by Hand\./i)).toBeInTheDocument();
});

test('switches storefront content to the selected language and remembers it', () => {
  localStorage.clear();
  render(<App />);

  fireEvent.change(screen.getByRole('combobox'), { target: { value: 'hi' } });

  expect(screen.getByText('मिट्टी से निर्मित, कारीगरों के हाथों से तराशा हुआ।')).toBeInTheDocument();
  expect(screen.queryByText('भारतीय कला रूप')).not.toBeInTheDocument();
  expect(localStorage.getItem('mittika_language')).toBe('hi');
});

test('shows a notification after adding a product to cart and wishlist', async () => {
  localStorage.setItem('token', 'customer-token');
  API.get.mockResolvedValue({
    data: { user: { userType: 'customer' } }
  });
  API.post.mockResolvedValue({ data: {} });

  render(<App />);

  fireEvent.click(screen.getByRole('link', { name: 'Jewellery' }));
  fireEvent.click((await screen.findAllByRole('button', { name: 'Add to Cart' }))[0]);
  expect(await screen.findByText('Product added to cart.')).toBeInTheDocument();

  fireEvent.click(screen.getAllByRole('button', { name: 'Wishlist' })[0]);
  expect(await screen.findByText('Product added to wishlist.')).toBeInTheDocument();
  expect(API.post).toHaveBeenCalledWith('/cart', expect.any(Object));
  expect(API.post).toHaveBeenCalledWith('/wishlist', expect.any(Object));
});

test('starts speech recognition from the microphone action and submits its transcript', () => {
  const recognition = {
    start: jest.fn(),
    stop: jest.fn(),
    abort: jest.fn()
  };
  window.SpeechRecognition = jest.fn(() => recognition);
  const onSearch = jest.fn();
  const { unmount } = render(
    <MemoryRouter>
      <VoiceSearchModal isOpen onClose={jest.fn()} onSearch={onSearch} />
    </MemoryRouter>
  );

  fireEvent.click(screen.getByRole('button', { name: 'Start voice search' }));
  expect(recognition.start).toHaveBeenCalledTimes(1);

  act(() => recognition.onresult({ results: [[{ transcript: 'pottery' }]] }));
  fireEvent.click(screen.getByRole('button', { name: 'Search "pottery"' }));
  expect(onSearch).toHaveBeenCalledWith('pottery');

  unmount();
  delete window.SpeechRecognition;
});

test('payment checkout uses the regular payment label without demo wording', async () => {
  API.get.mockResolvedValueOnce({
    data: { items: [{ id: 'item-1', title: 'Clay pot', price: 500, quantity: 1 }] }
  });

  render(
    <MemoryRouter>
      <DummyPayment user={{ name: 'Customer' }} />
    </MemoryRouter>
  );

  expect(await screen.findByRole('button', { name: 'Pay Now' })).toBeInTheDocument();
  expect(screen.queryByText(/demo/i)).not.toBeInTheDocument();
});

test('translates product names and descriptions into the selected language', async () => {
  API.post.mockResolvedValueOnce({
    data: { translations: ['मीनाकारी हार का सेट', 'त्योहारों के लिए रंगीन मीनाकारी से सजा हस्तनिर्मित हार।'] }
  });

  render(
    <LanguageContext.Provider value="hi">
      <ProductCard
        image="necklace.jpg"
        title="Meenakari Necklace Set"
        description="Handmade necklace with vibrant meenakari detailing."
      />
    </LanguageContext.Provider>
  );

  expect(await screen.findByText('मीनाकारी हार का सेट')).toBeInTheDocument();
  expect(screen.getByText('त्योहारों के लिए रंगीन मीनाकारी से सजा हस्तनिर्मित हार।')).toBeInTheDocument();
  expect(API.post).toHaveBeenCalledWith('/translations', {
    language: 'hi',
    texts: ['Meenakari Necklace Set', 'Handmade necklace with vibrant meenakari detailing.']
  });
});

test('shows original English product text when translation fails', async () => {
  const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {});
  API.post.mockRejectedValueOnce(new Error('Translation service unavailable'));

  render(
    <LanguageContext.Provider value="mr">
      <ProductCard
        image="necklace.jpg"
        title="Meenakari Necklace Set"
        description="Handmade necklace with vibrant meenakari detailing."
      />
    </LanguageContext.Provider>
  );

  expect(await screen.findByText('Meenakari Necklace Set')).toBeInTheDocument();
  expect(screen.getByText('Handmade necklace with vibrant meenakari detailing.')).toBeInTheDocument();
  expect(await screen.findByText('भाषांतर उपलब्ध नाही; उत्पादनाचे मूळ इंग्रजी वर्णन दाखवले आहे.')).toBeInTheDocument();
  consoleError.mockRestore();
});

test('does not show product-view controls or viewer copy', () => {
  render(
    <LanguageContext.Provider value="en">
      <ProductCard image="pot.jpg" title="Handmade Clay Vase" description="A handmade decorative vase." />
    </LanguageContext.Provider>
  );

  expect(screen.queryByRole('button', { name: /view/i })).not.toBeInTheDocument();
  expect(screen.queryByText(/inspector|spin the product photo/i)).not.toBeInTheDocument();
});

test('shows a localized translating status while product translation is pending', () => {
  API.post.mockImplementationOnce(() => new Promise(() => {}));

  render(
    <LanguageContext.Provider value="hi">
      <ProductCard
        image="necklace.jpg"
        title="Pending translation necklace"
        description="This product description is still being translated."
      />
    </LanguageContext.Provider>
  );

  expect(screen.getAllByText('उत्पाद का अनुवाद हो रहा है...')).toHaveLength(2);
  expect(screen.queryByText('Pending translation necklace')).not.toBeInTheDocument();
  expect(screen.queryByText('This product description is still being translated.')).not.toBeInTheDocument();
});

test.each([
  ['मिट्टी का मटका', 'pottery'],
  ['दागिने', 'jewellery'],
  ['पूजा थाली', 'spiritual'],
  ['मेणबत्ती', 'candle'],
  ['रुखवत', 'rukhwat'],
  ['गृह सजावट', 'home'],
  ['Pottery Art', 'pottery'],
  ['Handmade Jewellery', 'jewellery'],
  ['Rukhwat Art', 'rukhwat'],
  ['Candle and Resin Art', 'candle'],
  ['Spiritual Art', 'spiritual'],
  ['Home Decor', 'home'],
  ['Macrame & Woodwork', 'home']
])('maps multilingual query "%s" to %s', (query, category) => {
  expect(categoryForSearch(query)).toBe(category);
});
