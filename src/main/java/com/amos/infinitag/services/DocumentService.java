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

    public Iterable<Document> getAllDocuments() {
        return this.documentRepository.findAll();
    }

    public Optional<Document> getDocumentById(Integer id) {
        return this.documentRepository.findById(id);
    }

    public Document getDocumentByName(String name) {
        return this.documentRepository.findByName(name);
    }

    public Document saveDocument(Document document) {
        return this.documentRepository.save(document);
    }

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
