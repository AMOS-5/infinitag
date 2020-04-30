package com.amos.infinitag.integrationtests;

import com.amos.infinitag.models.Document;
import com.amos.infinitag.repositories.DocumentRepository;
import com.amos.infinitag.services.DocumentService;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Bean;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.context.junit4.SpringRunner;
import org.springframework.test.web.servlet.MockMvc;
import java.util.ArrayList;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@SpringBootTest
@AutoConfigureMockMvc
@RunWith(SpringRunner.class)
public class DocumentServiceTest {
    @Autowired
    private MockMvc mvc;

    @MockBean
    private DocumentRepository documentRepository;

    @TestConfiguration
    class DocumentServiceImplTestContextConfiguration {

        @Bean
        public DocumentService documentService() {
            return new DocumentService(documentRepository);
        }
    }

    @Autowired
    private DocumentService documentService;

    @Before
    public void setUp() {
        Document document = new Document();
        document.setName("DocumentServiceTest");
        document.setId(1);

        Document document2 = new Document();
        document2.setName("OtherTestName");

        ArrayList<Document> documents = new ArrayList<Document>();
        documents.add(document);
        documents.add(document2);

        when(documentRepository.findByName(document.getName()))
            .thenReturn(document);

        when(documentRepository.findById(document.getId()))
            .thenReturn(Optional.of(document));

        when(documentRepository.findAll())
            .thenReturn(documents);
    }

    @Test
    public void whenValidId_thenDocumentShouldBeFound() {
        Integer id = 1;
        Optional<Document> found = documentService.getDocumentById(id);

        assertFalse(found.isEmpty());
        Document doc = found.get();
        assertEquals(doc.getId(), id);
    }

    @Test
    public void whenValidName_thenDocumentShouldBeFound() {
        String name = "DocumentServiceTest";
        Document found = documentService.getDocumentByName(name);
        assertNotNull(found);
        assertEquals(found.getName(), name);
    }

    @Test
    public void fetchAllDocuments() {
        ArrayList<Document> documents = (ArrayList<Document>) documentService.getAllDocuments();
        assertNotNull(documents);
        int size = documents.size();
        assertNotEquals(size, 0);
    }

    @Test
    public void shouldSaveFile() {
        MockMultipartFile mockMultipartFile = new MockMultipartFile("user-file","filename",
            "text/plain", "test data".getBytes());

        Document document = new Document();
        document.setName("DocumentServiceTest");
        document.setId(1);
        when(documentRepository.save(any(Document.class))).thenReturn(document);
        Document saveDocument = documentService.saveDocument(mockMultipartFile, "Path", "Name");
        assertNotNull(saveDocument);

        Optional<Document> foundDocument = documentService.getDocumentById(saveDocument.getId());
        assertTrue(foundDocument.isPresent());

        Document found = foundDocument.get();
        assertEquals(found.getName(), document.getName());

    }


}
