package com.amos.infinitag.controllers;

import com.amos.infinitag.exceptions.StorageFileNotFoundException;
import com.amos.infinitag.models.Document;
import com.amos.infinitag.services.DocumentService;
import com.amos.infinitag.services.FileSystemStorageService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;


@RestController()
@CrossOrigin(origins = "http://localhost:4200")
public class DocumentController {

    private final FileSystemStorageService storageService;
    private final DocumentService documentService;

    @Autowired
    public DocumentController(FileSystemStorageService storageService, DocumentService documentService) {
        this.storageService = storageService;
        this.documentService = documentService;
    }

    /**
     *
     * @return Returns a collection of all documents in the database.
     */
    @GetMapping("/documents")
    public Iterable<Document> getDocuments() {
        Iterable<Document> documents = this.documentService.getAllDocuments();
        System.out.println(documents);
        return this.documentService.getAllDocuments();
    }

    /**
     * Loads the file and returns the content. Uses the original name of the file instead
     * of the UUID
     * @param filename Name (UUID) of the file to be fetched.
     * @return A response with the file as an attachment. Can be used in a download link
     * @throws IOException Throws an exception if the file does not exist or cannot be read.
     */
    @GetMapping(
        value = "/documents/download/{filename}",
        produces = MediaType.APPLICATION_OCTET_STREAM_VALUE)
    @ResponseBody
    public ResponseEntity<Resource> getFile(@PathVariable String filename) throws IOException {

        Path path = storageService.load(filename);
        ByteArrayResource byteArrayResource = new ByteArrayResource(Files.readAllBytes(path));
        Document document = this.documentService.getDocumentByName(filename);

        HttpHeaders headers = new HttpHeaders();
        headers.add("Cache-Control", "no-cache, no-store, must-revalidate");
        headers.add("Pragma", "no-cache");
        headers.add("Expires", "0");
        String dispositionHeader = "attachment; filename=".concat(document.getOriginalName());
        headers.add(HttpHeaders.CONTENT_DISPOSITION, dispositionHeader);

        return ResponseEntity.ok()
            .headers(headers)
            .contentLength(byteArrayResource.contentLength())
            .contentType(MediaType.APPLICATION_OCTET_STREAM)
            .body(byteArrayResource);
    }


    /**
     * Saves the file using the storage service and creates a new entry in the database.
     * The name of the file is replaced with a UUID to prevent conflicts.
     * @param file MultipartFile. The file has to be attached to the request with the 'file' label.
     * @return Document which has been created
     */
    @PostMapping("/documents/upload")
    public Document handleDocumentUpload(@RequestParam("file") MultipartFile file) {

        UUID uuid = UUID.randomUUID();
        String name = uuid.toString();
        String path = storageService.store(file, name);
        return documentService.saveDocument(file, path, name);
    }

    @ExceptionHandler(StorageFileNotFoundException.class)
    public ResponseEntity<?> handleStorageFileNotFound(StorageFileNotFoundException exc) {
        return ResponseEntity.notFound().build();
    }

}
