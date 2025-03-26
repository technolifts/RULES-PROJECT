import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import DocumentList from '@/components/DocumentList';
import DocumentUpload from '@/components/DocumentUpload';
import { AuthProvider } from '@/contexts/AuthContext';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
    };
  },
}));

// Mock axios
jest.mock('axios', () => ({
  post: jest.fn(),
  get: jest.fn(),
  delete: jest.fn(),
}));

const mockDocuments = [
  {
    id: 1,
    filename: 'test-file-1.pdf',
    original_filename: 'test-document-1.pdf',
    content_type: 'application/pdf',
    file_size: 1024,
    description: 'Test document 1',
    user_id: 1,
    created_at: '2023-12-01T12:00:00Z',
    updated_at: null
  },
  {
    id: 2,
    filename: 'test-file-2.docx',
    original_filename: 'test-document-2.docx',
    content_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    file_size: 2048,
    description: 'Test document 2',
    user_id: 1,
    created_at: '2023-12-02T12:00:00Z',
    updated_at: null
  }
];

const renderWithAuth = (component) => {
  return render(<AuthProvider>{component}</AuthProvider>);
};

describe('DocumentList Component', () => {
  it('renders document list correctly', () => {
    const onDelete = jest.fn();
    render(<DocumentList documents={mockDocuments} onDelete={onDelete} />);
    
    expect(screen.getByText('test-document-1.pdf')).toBeInTheDocument();
    expect(screen.getByText('test-document-2.docx')).toBeInTheDocument();
    expect(screen.getByText('Test document 1')).toBeInTheDocument();
    expect(screen.getByText('Test document 2')).toBeInTheDocument();
    
    // Check for delete buttons
    const deleteButtons = screen.getAllByText('Delete');
    expect(deleteButtons).toHaveLength(2);
  });

  it('handles delete confirmation flow', () => {
    const onDelete = jest.fn();
    render(<DocumentList documents={mockDocuments} onDelete={onDelete} />);
    
    // Click delete button for first document
    const deleteButtons = screen.getAllByText('Delete');
    fireEvent.click(deleteButtons[0]);
    
    // Confirm delete dialog should appear
    expect(screen.getByText('Confirm')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
    
    // Click confirm
    fireEvent.click(screen.getByText('Confirm'));
    
    // onDelete should be called with document id
    expect(onDelete).toHaveBeenCalledWith(1);
  });
});

describe('DocumentUpload Component', () => {
  it('renders upload form correctly', () => {
    const onClose = jest.fn();
    const onUploadSuccess = jest.fn();
    
    renderWithAuth(<DocumentUpload onClose={onClose} onUploadSuccess={onUploadSuccess} />);
    
    expect(screen.getByText('Upload Document')).toBeInTheDocument();
    expect(screen.getByText('File')).toBeInTheDocument();
    expect(screen.getByText('Description (optional)')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
    expect(screen.getByText('Upload')).toBeInTheDocument();
  });

  it('handles form submission', async () => {
    const onClose = jest.fn();
    const onUploadSuccess = jest.fn();
    
    renderWithAuth(<DocumentUpload onClose={onClose} onUploadSuccess={onUploadSuccess} />);
    
    // Fill in description
    const descriptionInput = screen.getByLabelText('Description (optional)');
    fireEvent.change(descriptionInput, { target: { value: 'Test upload description' } });
    
    // Submit form without file should show error
    fireEvent.click(screen.getByText('Upload'));
    
    await waitFor(() => {
      expect(screen.getByText('Please select a file to upload')).toBeInTheDocument();
    });
  });
});
