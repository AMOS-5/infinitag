package com.amos.infinitag.repositories;

import com.amos.infinitag.models.Document;
import org.springframework.data.jpa.repository.JpaRepository;

public interface DocumentRepository extends JpaRepository<Document, Integer> {
    public Document findByName(String name);

    public Document findByOriginalName(String originalName);
}
