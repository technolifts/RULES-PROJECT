import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ShareDocument from '@/components/ShareDocument';
import SharesList from '@/components/SharesList';
import { AuthProvider } from '@/contexts/AuthContext';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
    };
  },
  useParams() {
    return {
      token: 'test-token',
    };
  },
}));

// Mock axios
jest.mock('axios', () => ({
  post: jest.fn(() => Promise.resolve({ data: { token: 'test-token' } })),
  get: jest.fn(() => Promise.resolve({ data: [] })),
  delete: jest.fn(),
}));

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: jest.fn(),
  },
});

const mockDocument = {
  id: 1,
  filename: 'test-file.pdf',
  original_filename: 'test-document.pdf',
  content_type: 'application/pdf',
  file_size: 1024,
  description: 'Test document',
  user_id: 1,
  created_at: '2023-12-01T12:00:00Z',
  updated_at: null
};

const renderWithAuth = (component) => {
  return render(<AuthProvider>{component}</AuthProvider>);
};

describe('ShareDocument Component', () => {
  it('renders share form correctly', () => {
    const onClose = jest.fn();
    const onShareSuccess = jest.fn();
    
    renderWithAuth(
      <ShareDocument 
        document={mockDocument} 
        onClose={onClose} 
        onShareSuccess={onShareSuccess} 
      />
    );
    
    expect(screen.getByText('Share Document')).toBeInTheDocument();
    expect(screen.getByText(/You are sharing:/)).toBeInTheDocument();
    expect(screen.getByText('test-document.pdf')).toBeInTheDocument();
    expect(screen.getByText('Link expires after (days)')).toBeInTheDocument();
    expect(screen.getByText('Create Share Link')).toBeInTheDocument();
  });

  it('allows selecting expiry period', () => {
    const onClose = jest.fn();
    const onShareSuccess = jest.fn();
    
    renderWithAuth(
      <ShareDocument 
        document={mockDocument} 
        onClose={onClose} 
        onShareSuccess={onShareSuccess} 
      />
    );
    
    const expirySelect = screen.getByLabelText('Link expires after (days)');
    fireEvent.change(expirySelect, { target: { value: '30' } });
    
    expect(expirySelect).toHaveValue('30');
  });
});

describe('SharesList Component', () => {
  it('renders loading state', () => {
    const onClose = jest.fn();
    const onRefreshShares = jest.fn();
    
    renderWithAuth(
      <SharesList 
        onClose={onClose} 
        onRefreshShares={onRefreshShares} 
      />
    );
    
    expect(screen.getByText('Manage Shared Links')).toBeInTheDocument();
    // Should show loading spinner initially
    expect(screen.getByRole('status')).toBeInTheDocument();
  });
});
