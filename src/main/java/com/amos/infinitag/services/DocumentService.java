package com.amos.infinitag.services;

import com.amos.infinitag.models.Document;
import com.amos.infinitag.repositories.DocumentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import java.time.LocalDate;
import java.util.Optional;

@Service
public class DocumentService {
    private final DocumentRepository documentRepository;

    @Autowired
    public DocumentService(DocumentRepository documentRepository) {
        this.documentRepository = documentRepository;
    }

    /**
     *
     * @return returns all documents in repository
     */
    public Iterable<Document> getAllDocuments() {
        return this.documentRepository.findAll();
    }

    /**
     * Gets a Document using its integer ID
     * @param id ID of the document
     * @return A document if it exists in the repository
     */
    public Optional<Document> getDocumentById(Integer id) {
        return this.documentRepository.findById(id);
    }

    /**
     * Gets a document from the repository given its name (UUID)
     * @param name UUID of the document.
     * @return Returns the document from the repository
     */
    public Document getDocumentByName(String name) {
        return this.documentRepository.findByName(name);
    }

    /**
     * Saves a document to the repository
     * @param document Document to be saved
     * @return Returns the saved document
     */
    public Document saveDocument(Document document) {
        return this.documentRepository.save(document);
    }

    /**
     * Converts a file to a Document and saves it to the database.
     * @param file MultipartFile from a post request
     * @param path Path where the file will be saved on the storage system
     * @param name Name of the file (UUID)
     * @return Returns the saved file.
     */
    public Document saveDocument(MultipartFile file, String path, String name) {
        String createdAt = LocalDate.now().toString();
        Document document = new Document();
        String originalFilename = file.getOriginalFilename();
        String fileType = "Unknown";
        if (originalFilename != null) {
            fileType = originalFilename.substring(originalFilename.lastIndexOf(".") + 1);
        }
        document.setName(name);
        document.setOriginalName(originalFilename);
        document.setSize(file.getSize());
        document.setCreatedAt(createdAt);
        document.setType(fileType);
        document.setPath(path);

        return documentRepository.save(document);


    }


}
