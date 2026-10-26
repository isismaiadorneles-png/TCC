import { StatusBar } from "expo-status-bar";
import { useState } from "react";
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  ScrollView,
} from "react-native";
import axios from "axios";

const GROQ_API_KEY = "";

export default function App() {
  const [ingredientes, setIngredientes] = useState("");
  const [receita, setReceita] = useState("");

  const api = axios.create({
    baseURL: "https://api.groq.com/openai/v1/",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${GROQ_API_KEY}`,
    },
  });

  async function gerarReceita() {
    try {
      const resposta = await api.post("chat/completions", {
        model: "openai/gpt-oss-20b",
        temperature: 1,
        max_tokens: 1024,
        messages: [
          {
            role: "system",
            content: `Você é um chef de cozinha muito criativo. Crie receitas deliciosas com que eu preciso. Responda em Português Brasil.
          🍽️ [NOME DA RECEITA EM MAIÚSCULO]
          ⏱️ Tempo: [tempo de preparo]
          👥 Porções: [quantidade]
          🧾 INGREDIENTES:
          - [Ingrediente 1]
          - [Ingrediente 2]
          👨‍🍳 MODO DE PREPARO:
          1. [passo 1]
          2. [passo 2]
          💡 DICA: [uma dica especial sobre a receita]`,
          },
          {
            role: "user",
            content: `Crie uma receita com esses Ingredientes: ${ingredientes}`,
          },
        ],
      });

      console.log("Resposta da API:", resposta.data);
      setReceita(
        resposta.data.choices[0].message?.content ||
          "Não foi possível gerar a receita.",
      );
    } catch (error) {
      console.error(
        "Erro ao gerar receita:",
        error.response?.data || error.message,
      );
    }
  }

  return (
    <View style={styles.container}>
      <StatusBar style="light" />

      <View style={styles.header}>
        <Text style={styles.emoji}>🧑‍🍳</Text>
        <Text style={styles.title}>Chef IA</Text>
        <Text style={styles.subTitle}>Digite seus Ingredientes</Text>
      </View>

      <TextInput
        style={styles.input}
        placeholder="Ex: Frango, arroz, tomate, cebola..."
        multiline
        placeholderTextColor="#888"
        value={ingredientes}
        onChangeText={setIngredientes}
      />

      <TouchableOpacity style={styles.button} onPress={gerarReceita}>
        <Text style={styles.buttonTxt}>Gerar Receitas</Text>
      </TouchableOpacity>

      {receita ? (
        <View style={styles.receitaWrapper}>
          <View style={styles.receitaHeader}>
            <Text style={styles.receitaHeaderText}>Sua Receita</Text>
          </View>

          <ScrollView style={styles.receitaContainer}>
            <Text style={styles.receita}>{receita}</Text>
          </ScrollView>
        </View>
      ) : (
        <View style={styles.placeholderContainer}>
          <Text style={styles.placeholderEmoji}>🍲</Text>
          <Text style={styles.placeholderText}>
            Sua Receita aparecerá aqui!
          </Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#1a1a2e",
    paddingHorizontal: 20,
  },
  header: {
    alignItems: "center",
    paddingTop: 60,
    paddingBottom: 20,
  },
  emoji: {
    fontSize: 50,
    marginBottom: 10,
  },
  title: {
    fontSize: 32,
    marginBottom: 10,
    color: "#ffffff",
    fontWeight: "bold",
  },
  subTitle: {
    fontSize: 14,
    color: "#888",
    marginTop: 5,
  },
  input: {
    backgroundColor: "#2d2d44",
    borderRadius: 15,
    padding: 15,
    fontSize: 16,
    color: "#fff",
    minHeight: 80,
    textAlignVertical: "top",
    marginBottom: 15,
  },
  button: {
    backgroundColor: "#e17055",
    paddingVertical: 16,
    borderRadius: 15,
    alignItems: "center",
    marginBottom: 15,
  },
  buttonTxt: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "bold",
  },
  receitaWrapper: {
    flex: 1,
    marginBottom: 30,
    borderRadius: 20,
    overflow: "hidden",
    backgroundColor: "#2d2d44",
  },
  receitaHeader: {
    backgroundColor: "#e17055",
    paddingVertical: 12,
    paddingHorizontal: 15,
  },
  receitaHeaderText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "bold",
    textAlign: "center",
  },
  receitaContainer: {
    flex: 1,
    padding: 20,
  },
  receita: {
    color: "#fff",
    fontSize: 16,
    lineHeight: 26,
  },
  placeholderContainer: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  placeholderEmoji: {
    fontSize: 60,
    marginBottom: 15,
  },
  placeholderText: {
    color: "#666",
    fontSize: 16,
    textAlign: "center",
  },
});
