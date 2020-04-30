package com.amos.infinitag.unittests;

import java.nio.file.Paths;
import java.util.stream.Stream;

import com.amos.infinitag.exceptions.StorageFileNotFoundException;
import com.amos.infinitag.services.FileSystemStorageService;
import org.junit.jupiter.api.Test;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.web.servlet.MockMvc;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.BDDMockito.given;
import static org.mockito.BDDMockito.then;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;


@AutoConfigureMockMvc
@SpringBootTest
public class DocumentUploadTest {

    @Autowired
    private MockMvc mvc;

    @MockBean
    private FileSystemStorageService storageService;

    @Test
    public void shouldSaveUploadedFile() throws Exception {
        MockMultipartFile multipartFile = new MockMultipartFile("file", "test.txt",
            "text/plain", "Spring Framework".getBytes());
        this.mvc.perform(multipart("/documents/upload").file(multipartFile))
            .andExpect(status().isOk());

    }

    @SuppressWarnings("unchecked")
    @Test
    public void should404WhenMissingFile() throws Exception {
        given(this.storageService.loadAsResource("test.txt"))
            .willThrow(StorageFileNotFoundException.class);

        this.mvc.perform(get("/documents/test.txt")).andExpect(status().isNotFound());
    }

}
