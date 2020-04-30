package com.amos.infinitag.integrationtests;

import com.amos.infinitag.models.Document;
import com.amos.infinitag.repositories.DocumentRepository;
import com.amos.infinitag.services.FileSystemStorageService;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.junit4.SpringRunner;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

@RunWith(SpringRunner.class)
@AutoConfigureTestDatabase(replace= AutoConfigureTestDatabase.Replace.NONE)
@DataJpaTest
public class DocumentRepositoryIntegrationTest {

    @Autowired
    private TestEntityManager entityManager;

    @Autowired
    private DocumentRepository documentRepository;

    @MockBean
    private FileSystemStorageService storageService;

    @Test
    public void return_document_by_id() {
        Document document = new Document();
        document.setName("Test");
        entityManager.persistAndFlush(document);

        Optional<Document> found = documentRepository.findById(document.getId());

        assertFalse(found.isEmpty());
        assertEquals(document.getName(), found.get().getName());

    }

    @Test
    public void return_document_by_name() {
        Document document = new Document();
        document.setName("Test2");
        entityManager.persistAndFlush(document);

        Document found = documentRepository.findByName(document.getName());
        assertEquals(found.getName(), document.getName());
    }


}
